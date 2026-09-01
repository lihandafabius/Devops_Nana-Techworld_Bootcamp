import requests
import smtplib
import os
import paramiko
import boto3
import schedule

import time
from datetime import datetime



EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')

ec2_client = boto3.client('ec2', region_name ='eu-north-1')

INSTANCE_ID = ""
SERVER_IP = ""
SSH_USERNAME = "ubuntu"
APP_URL = f"http://{SERVER_IP}:8080/"
SSH_KEY = "path-to-key-pair.pem"
CONTAINER_NAME = 'nice_bohr'

# check application
def check_application():
    try:
        response = requests.get(APP_URL,timeout=10)
        print(f"Application HTTP Status: {response.status_code}")

        return response.status_code == 200

    except requests.exceptions.RequestException as ex:
        print(f"Application connection error: {ex}")

        return False


# check ec2 status
def check_instance_status():
    response = ec2_client.describe_instance_status(InstanceIds=[INSTANCE_ID], IncludeAllInstances=True)
    statuses = response["InstanceStatuses"]

    if not statuses:
        print("Could not retrieve EC2 status.")
        return False

    instance = statuses[0]
    instance_state = instance["InstanceState"]["Name"]
    instance_status = instance["InstanceStatus"]["Status"]
    system_status = instance["SystemStatus"]["Status"]

    print(f"""
            EC2 Status
            ----------------
            Instance State: {instance_state}
            Instance Check: {instance_status}
            System Check: {system_status}
    """)

    return (instance_state == "running" and instance_status == "ok" and system_status == "ok")

def restart_application():
    # restart the application
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(
            paramiko.AutoAddPolicy())  # confirm interactive mode missing host key prompt to llow connection
        ssh.connect(SERVER_IP, username=SSH_USERNAME, key_filename=SSH_KEY, timeout=10, banner_timeout=10, auth_timeout=10)

        stdin, stdout, stderr = ssh.exec_command(f'sudo docker restart {CONTAINER_NAME}')
        output = stdout.read().decode()
        error = stderr.read().decode()
        ssh.close()

        print(output)
        if error:
            print(error)

        print("Application restarted!")

        return True

    except Exception as ex:
        print(f"Failed to restart application: {ex}")
        return False


def send_email_notification(email_msg):
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.ehlo()
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        msg = f"Subject: SITE DOWN\n{email_msg}"
        smtp.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, msg)

def reboot_instance():
    try:
        print( "Rebooting EC2 instance...")

        ec2_client.reboot_instances(InstanceIds=[INSTANCE_ID])
        print("Waiting for EC2 to become healthy...")

        waiter = ec2_client.get_waiter("instance_status_ok")
        waiter.wait(InstanceIds=[INSTANCE_ID] )

        print("EC2 instance is healthy.")

        return True


    except Exception as ex:
        print(f"Failed to reboot EC2: {ex}")

        return False


def monitoring():

    try:
        print("Check Application")
        application_healthy = check_application()

        if application_healthy:
            print("Application is up and running!")

        else:
            print("Application is down! Fix it!")
            # send email
            msg = "Application health check failed. Fix the issue!"
            send_email_notification(msg)

            # check EC2 health
            ec2_healthy = check_instance_status()

            if ec2_healthy:
                print("EC2 instance is healthy, restarting docker container")
                # restart application
                restart_success = restart_application()

                if not restart_success:
                    print("Application restart failed!")

            else:
                print("EC2 instance is unhealthy")
                reboot_success = reboot_instance()

                if reboot_success:
                    print("Checking Application after EC2 recovery")
                    check_application()


    except Exception as ex:
        print(f'Connection error happened: {ex}')
        msg = "Application Not Accessible Fix the issue!"
        send_email_notification(msg)

        # restart ubuntu server
        try:
            print("Rebooting EC2 instance...")
            ec2_client.reboot_instances(InstanceIds=[INSTANCE_ID])
        except Exception as ex:
            print(f"Failed to reboot EC2: {ex}")
        # restart the application
        restart_application()

time_now = datetime.now()
schedule.every(5).seconds.do(monitoring)

print(f"Application Monitoring Started at {time_now}")

while True:
    schedule.run_pending()
    time.sleep(1)