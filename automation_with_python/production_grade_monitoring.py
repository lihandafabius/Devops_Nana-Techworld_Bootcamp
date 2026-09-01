"""
EC2 application watchdog .

Periodically checks that a web app on an EC2 instance is reachable.
On sustained failure it escalates:
  email alert -> restart the docker container via SSH
  -> if the instance itself is unhealthy, reboot EC2 -> re-check -> alert if still down

Run as a long-lived process (see the included systemd unit).

Configuration is entirely via environment variables — see .env.example.
"""

from __future__ import annotations

import logging
import logging.handlers
import os
import signal
import smtplib
import sys
import time
from datetime import datetime, timezone
from email.mime.text import MIMEText

import boto3
import paramiko
import requests
import schedule
from botocore.exceptions import ClientError, WaiterError

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------
def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
ALERT_TO = os.environ.get("ALERT_TO", EMAIL_ADDRESS)

AWS_REGION = os.environ.get("AWS_REGION", "eu-north-1")
INSTANCE_ID = _require_env("EC2_INSTANCE_ID")
SSH_USERNAME = os.environ.get("SSH_USERNAME", "ubuntu")
SSH_KEY = _require_env("SSH_KEY_PATH")
CONTAINER_NAME = os.environ.get("CONTAINER_NAME", "nice_bohr")
APP_PORT = os.environ.get("APP_PORT", "8080")
APP_PATH = os.environ.get("APP_PATH", "/")

# If your instance doesn't have an Elastic IP, its public IP can change
# after a reboot. When true, we look the current IP up from EC2 instead
# of trusting a hardcoded value.
RESOLVE_IP_DYNAMICALLY = os.environ.get("RESOLVE_IP_DYNAMICALLY", "true").lower() == "true"
STATIC_SERVER_IP = os.environ.get("EC2_SERVER_IP")  # used if RESOLVE_IP_DYNAMICALLY is false

CHECK_INTERVAL_SECONDS = int(os.environ.get("CHECK_INTERVAL_SECONDS", "60"))
# Require this many consecutive failed checks before we treat the app as
# actually down — avoids reacting to a single transient blip.
FAILURE_THRESHOLD = int(os.environ.get("FAILURE_THRESHOLD", "2"))
# After taking a recovery action, wait at least this long before taking
# another, so we don't stack restarts/reboots on top of each other.
ACTION_COOLDOWN_SECONDS = int(os.environ.get("ACTION_COOLDOWN_SECONDS", "180"))

LOG_DIR = os.environ.get("LOG_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs"))
LOG_FILE = os.path.join(LOG_DIR, "watchdog.log")

# --------------------------------------------------------------------------
# Logging
# --------------------------------------------------------------------------
os.makedirs(LOG_DIR, exist_ok=True)

log = logging.getLogger("watchdog")
log.setLevel(logging.INFO)

_fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

_console = logging.StreamHandler(sys.stdout)
_console.setFormatter(_fmt)
log.addHandler(_console)

_file = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=5)
_file.setFormatter(_fmt)
log.addHandler(_file)

ec2_client = boto3.client("ec2", region_name=AWS_REGION)

# --------------------------------------------------------------------------
# State
# --------------------------------------------------------------------------
_consecutive_failures = 0
_last_action_time = 0.0
_running = True


def _in_cooldown() -> bool:
    return (time.time() - _last_action_time) < ACTION_COOLDOWN_SECONDS


def _mark_action_taken() -> None:
    global _last_action_time
    _last_action_time = time.time()


# --------------------------------------------------------------------------
# EC2 helpers
# --------------------------------------------------------------------------
def get_server_ip() -> str | None:
    if not RESOLVE_IP_DYNAMICALLY:
        return STATIC_SERVER_IP
    try:
        resp = ec2_client.describe_instances(InstanceIds=[INSTANCE_ID])
        reservations = resp.get("Reservations", [])
        if not reservations or not reservations[0]["Instances"]:
            log.error("No instance data returned for %s", INSTANCE_ID)
            return None
        instance = reservations[0]["Instances"][0]
        return instance.get("PublicIpAddress")
    except ClientError as ex:
        log.error("Failed to resolve instance IP: %s", ex)
        return None


def check_instance_status() -> bool:
    try:
        response = ec2_client.describe_instance_status(
            InstanceIds=[INSTANCE_ID], IncludeAllInstances=True
        )
    except ClientError as ex:
        log.error("Could not query EC2 status: %s", ex)
        return False

    statuses = response.get("InstanceStatuses", [])
    if not statuses:
        log.warning("Could not retrieve EC2 status (no data returned).")
        return False

    instance = statuses[0]
    instance_state = instance["InstanceState"]["Name"]
    instance_status = instance["InstanceStatus"]["Status"]
    system_status = instance["SystemStatus"]["Status"]

    log.info(
        "EC2 status - state=%s instance_check=%s system_check=%s",
        instance_state, instance_status, system_status,
    )
    return instance_state == "running" and instance_status == "ok" and system_status == "ok"


def reboot_instance() -> bool:
    try:
        log.warning("Rebooting EC2 instance %s ...", INSTANCE_ID)
        ec2_client.reboot_instances(InstanceIds=[INSTANCE_ID])

        log.info("Waiting for EC2 status checks to pass...")
        waiter = ec2_client.get_waiter("instance_status_ok")
        waiter.wait(InstanceIds=[INSTANCE_ID], WaiterConfig={"Delay": 15, "MaxAttempts": 40})

        log.info("EC2 instance is healthy after reboot.")
        # Status checks passing doesn't guarantee SSH/docker are ready yet.
        time.sleep(15)
        return True
    except WaiterError as ex:
        log.error("Timed out waiting for EC2 to become healthy: %s", ex)
        return False
    except Exception as ex:
        log.error("Failed to reboot EC2: %s", ex)
        return False


# --------------------------------------------------------------------------
# Application / SSH helpers
# --------------------------------------------------------------------------
def check_application(server_ip: str) -> tuple[bool, str]:
    url = f"http://{server_ip}:{APP_PORT}{APP_PATH}"
    try:
        response = requests.get(url, timeout=10)
        healthy = response.status_code == 200
        detail = f"HTTP {response.status_code}"
        log.info("Application check (%s): %s", url, detail)
        return healthy, detail
    except requests.exceptions.RequestException as ex:
        log.warning("Application connection error (%s): %s", url, ex)
        return False, str(ex)


def restart_application(server_ip: str) -> bool:
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            server_ip,
            username=SSH_USERNAME,
            key_filename=SSH_KEY,
            timeout=10,
            banner_timeout=10,
            auth_timeout=10,
        )

        _stdin, stdout, stderr = ssh.exec_command(f"sudo docker restart {CONTAINER_NAME}")
        exit_status = stdout.channel.recv_exit_status()
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()
        ssh.close()

        if output:
            log.info("docker restart output: %s", output)
        if error:
            log.warning("docker restart stderr: %s", error)

        if exit_status != 0:
            log.error("docker restart failed with exit status %s", exit_status)
            return False

        log.info("Application container restarted successfully.")
        return True

    except Exception as ex:
        log.error("Failed to restart application via SSH: %s", ex)
        return False


# --------------------------------------------------------------------------
# Alerting
# --------------------------------------------------------------------------
def send_email_notification(subject: str, body: str) -> None:
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD or not ALERT_TO:
        log.warning("Email not configured - skipping alert. Subject=%r Body=%r", subject, body)
        return
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = ALERT_TO

        with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as smtp:
            smtp.starttls()
            smtp.ehlo()
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.sendmail(EMAIL_ADDRESS, [ALERT_TO], msg.as_string())
        log.info("Alert email sent: %s", subject)
    except Exception as ex:
        # A notification failure must never take down the watchdog.
        log.error("Failed to send alert email: %s", ex)


# --------------------------------------------------------------------------
# Main monitoring cycle
# --------------------------------------------------------------------------
def monitoring() -> None:
    global _consecutive_failures

    server_ip = get_server_ip()
    if not server_ip:
        log.error("Could not determine server IP this cycle - skipping.")
        return

    healthy, detail = check_application(server_ip)

    if healthy:
        if _consecutive_failures > 0:
            log.info("Application recovered after %d failed check(s).", _consecutive_failures)
        _consecutive_failures = 0
        return

    _consecutive_failures += 1
    log.warning(
        "Application check failed (%s). Consecutive failures: %d/%d",
        detail, _consecutive_failures, FAILURE_THRESHOLD,
    )

    if _consecutive_failures < FAILURE_THRESHOLD:
        return  # not yet convinced this is a real outage

    if _in_cooldown():
        log.info(
            "Recovery action taken within the last %ss - skipping further action this cycle.",
            ACTION_COOLDOWN_SECONDS,
        )
        return

    send_email_notification(
        "SITE DOWN",
        f"[{datetime.now(timezone.utc).isoformat()}] Application unreachable "
        f"({_consecutive_failures} consecutive failures): {detail}. Attempting recovery.",
    )

    ec2_healthy = check_instance_status()

    if ec2_healthy:
        log.info("EC2 instance is healthy - restarting the docker container.")
        _mark_action_taken()
        if not restart_application(server_ip):
            send_email_notification(
                "SITE DOWN - restart failed",
                "Docker container restart via SSH failed. Manual intervention needed.",
            )
    else:
        log.warning("EC2 instance is unhealthy - rebooting.")
        _mark_action_taken()
        if reboot_instance():
            new_ip = get_server_ip() or server_ip
            log.info("Re-checking application after EC2 recovery...")
            still_healthy, _ = check_application(new_ip)
            if not still_healthy:
                restart_application(new_ip)
        else:
            send_email_notification(
                "SITE DOWN - reboot failed",
                "EC2 reboot attempt failed. Manual intervention needed.",
            )

    _consecutive_failures = 0  # reset after taking action; next cycle re-evaluates fresh


# --------------------------------------------------------------------------
# Graceful shutdown
# --------------------------------------------------------------------------
def _handle_shutdown(signum, _frame):
    global _running
    log.info("Received signal %s - shutting down.", signum)
    _running = False


def main() -> None:
    signal.signal(signal.SIGINT, _handle_shutdown)
    signal.signal(signal.SIGTERM, _handle_shutdown)

    log.info(
        "Watchdog started. interval=%ss failure_threshold=%s cooldown=%ss dynamic_ip=%s",
        CHECK_INTERVAL_SECONDS, FAILURE_THRESHOLD, ACTION_COOLDOWN_SECONDS, RESOLVE_IP_DYNAMICALLY,
    )
    schedule.every(CHECK_INTERVAL_SECONDS).seconds.do(monitoring)

    while _running:
        try:
            schedule.run_pending()
        except Exception as ex:
            log.error("Unhandled error in monitoring cycle: %s", ex, exc_info=True)
        time.sleep(1)

    log.info("Watchdog stopped.")


if __name__ == "__main__":
    main()