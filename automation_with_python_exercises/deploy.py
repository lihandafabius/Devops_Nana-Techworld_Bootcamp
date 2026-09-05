import paramiko
import sys

server_ip = "13.60.211.189"

ecr_registry = "480007295919.dkr.ecr.eu-north-1.amazonaws.com"
repository = "java-maven-app"

ports = {
    "1.0": 3000,
    "2.0": 80,
    "3.0": 8080
}


def ssh_into_ec2_and_start_container(
    tag,
    image_digest,
    ecr_password,
    ssh_username,
    ssh_key
):

    ssh = None

    try:
        ssh = paramiko.SSHClient()

        ssh.set_missing_host_key_policy(
            paramiko.AutoAddPolicy()
        )

        ssh.connect(
            server_ip,
            username=ssh_username,
            key_filename=ssh_key,
            timeout=10,
            banner_timeout=10,
            auth_timeout=10
        )

        host_port = ports[tag]

        command = f"""
set -e

docker login \
    --username AWS \
    --password-stdin {ecr_registry}

docker pull {ecr_registry}/{repository}@{image_digest}

docker rm -f java-maven-app 2>/dev/null || true

docker run -d \
    --name java-maven-app \
    -p {host_port}:{host_port} \
    {ecr_registry}/{repository}@{image_digest}
"""

        stdin, stdout, stderr = ssh.exec_command(command)

        # Send the ECR password to docker login through stdin.
        stdin.write(ecr_password + "\n")
        stdin.flush()
        stdin.channel.shutdown_write()

        output = stdout.read().decode()
        error = stderr.read().decode()
        exit_status = stdout.channel.recv_exit_status()

        print(output)

        if error:
            print(error)

        if exit_status != 0:
            print(
                f"Remote deployment failed with exit code "
                f"{exit_status}"
            )
            return False

        print(f"Image {tag} deployed successfully.")
        print(f"Application available on port {host_port}")

        return True

    except Exception as ex:
        print(
            f"Failed to deploy application: "
            f"{type(ex).__name__}: {ex}"
        )
        return False

    finally:
        if ssh:
            ssh.close()


if __name__ == "__main__":

    if len(sys.argv) != 5:
        print(
            "Usage: python deploy.py "
            "'<tag>|<digest>' "
            "'<ecr_password>' "
            "'<ssh_username>' "
            "'<ssh_key_path>'"
        )
        sys.exit(1)

    selected_image = sys.argv[1]
    ecr_password = sys.argv[2]
    ssh_username = sys.argv[3]
    ssh_key = sys.argv[4]

    tag, image_digest = selected_image.split("|", 1)

    print(f"Selected image tag: {tag}")
    print(f"Selected image digest: {image_digest}")

    if tag not in ports:
        print(f"Unsupported image tag: {tag}")
        sys.exit(1)

    success = ssh_into_ec2_and_start_container(
        tag,
        image_digest,
        ecr_password,
        ssh_username,
        ssh_key
    )

    if not success:
        sys.exit(1)