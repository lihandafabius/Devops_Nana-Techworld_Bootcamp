import boto3
import paramiko
import requests
import time

def get_default_vpc():
    default_vpc = ec2_client.describe_vpcs(
        Filters=[
            {
                "Name": "is-default",
                "Values": ["true"]
            },
        ]
    )

    vpc_id = default_vpc['Vpcs'][0]['VpcId']
    return vpc_id


# Find a subnet in the default VPC
def get_default_subnets():
    vpc_id = get_default_vpc()
    subnets = ec2_client.describe_subnets(
        Filters=[
            {
                "Name": "vpc-id",
                "Values": [vpc_id]
            }
        ]
    )

    subnet_id = subnets['Subnets'][0]['SubnetId']
    return subnet_id


# Create EC2 instance
def create_ec2_instance():
    subnet_id = get_default_subnets()
    response = ec2_client.run_instances(
        ImageId="ami-0aba19e56f3eaec05",
        InstanceType="t3.micro",
        MinCount=1,
        MaxCount=1,
        KeyName="myapp-key-pair",
        SubnetId=subnet_id
    )
    instance_id = response["Instances"][0]["InstanceId"]
    return instance_id


# Check EC2 Status
def check_instance_status():
    while True:
        response = ec2_client.describe_instance_status(
            InstanceIds=[instance_id],
            IncludeAllInstances=True
        )

        statuses = response["InstanceStatuses"]

        if not statuses:
            print("Could not retrieve EC2 status.")
            time.sleep(5)
            continue

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

        if (instance_state == "running" and instance_status == "ok" and system_status == "ok"):
            return True

        print("EC2 instance is not ready. Checking again in 5 seconds...")
        time.sleep(5)


# Get public address
def get_server_ip():
    check_instance_status()

    response = ec2_client.describe_instances(
        InstanceIds=[instance_id]
    )

    instance = response["Reservations"][0]["Instances"][0]

    server_ip = instance.get("PublicIpAddress")

    return server_ip


# Get security group id
def get_security_group_id():
    response = ec2_client.describe_instances(
        InstanceIds=[instance_id]
    )

    instance = response["Reservations"][0]["Instances"][0]

    security_group_id = instance["SecurityGroups"][0]["GroupId"]

    return security_group_id


# Open sg port
def open_port(port):
    try:
        security_group_id = get_security_group_id()

        ec2_client.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[
                {
                    "IpProtocol": "tcp",
                    "FromPort": port,
                    "ToPort": port,
                    "IpRanges": [
                        {
                            "CidrIp":f"{my_ip}/32",
                            "Description": f"Allow port {port} traffic"
                        }
                    ]
                }
            ]
        )

        print(f"Port {port} opened successfully!")
        return True

    except ec2_client.exceptions.ClientError as ex:
        if "InvalidPermission.Duplicate" in str(ex):
            print(f"Port {port} is already open.")
            return True

        print(f"Failed to open port {port}: {ex}")
        return False


# Install docker and start nginx container
def install_docker_and_start_nginx():
    try:

        print("Installing Docker and starting nginx ...")
        server_ip = get_server_ip()
        if not server_ip:
            print("Could not retrieve the EC2 public IP.")
            return False

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # confirm interactive mode missing host key prompt to allow connection
        ssh.connect(server_ip, username=ssh_username, key_filename=ssh_key, timeout=10, banner_timeout=10, auth_timeout=10)

        command = """
sudo apt update &&
sudo apt install -y ca-certificates curl &&
sudo install -m 0755 -d /etc/apt/keyrings &&
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
    -o /etc/apt/keyrings/docker.asc &&
sudo chmod a+r /etc/apt/keyrings/docker.asc &&
sudo tee /etc/apt/sources.list.d/docker.sources > /dev/null <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF
sudo apt update &&
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin &&
sudo systemctl enable --now docker &&
sudo docker run -d --name nginx -p 80:80 nginx
"""

        stdin, stdout, stderr = ssh.exec_command(command)

        exit_status = stdout.channel.recv_exit_status()

        output = stdout.read().decode()
        error = stderr.read().decode()

        ssh.close()

        print(output)

        if exit_status == 0:
            print("Docker installed and Nginx container started successfully!")
            return True
        else:
            print("Docker installation failed!")
            print(error)
            return False

    except Exception as ex:
        print(f"Failed to install Docker: {ex}")
        return False


# Restart the nginx application
def restart_application():
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh.connect(server_ip, username=ssh_username, key_filename=ssh_key, timeout=10, banner_timeout=10, auth_timeout=10)
        stdin, stdout, stderr = ssh.exec_command("sudo docker restart nginx")

        exit_status = stdout.channel.recv_exit_status()

        output = stdout.read().decode()
        error = stderr.read().decode()

        ssh.close()

        print(output)

        if exit_status == 0:
            print("Application restarted!")
            return True
        else:
            print("Failed to restart application!")
            print(error)
            return False

    except Exception as ex:
        print(f"Failed to restart application: {ex}")
        return False


# Check whether Nginx is accessible
def check_application_status(app_url):
    for attempt in range(5):
        try:
            response = requests.get(app_url, timeout=10)

            print(f"Application HTTP Status: {response.status_code}")

            if response.status_code == 200:
                return True

        except requests.exceptions.RequestException as ex:
            print(f"Attempt {attempt + 1}: Nginx not ready yet.")

        time.sleep(3)

    return False


ec2_client = boto3.client("ec2", region_name="eu-north-1")

instance_id = create_ec2_instance()

ssh_username = "ubuntu"
ssh_key = "/home/fabius-lihanda/Downloads/myapp-key-pair.pem"

server_ip = get_server_ip()

my_ip = requests.get("https://api.ipify.org", timeout=10).text.strip()
if server_ip:
    open_port(22)  # SSH
    open_port(80)  # HTTP

    app_url = f"http://{server_ip}"

    if install_docker_and_start_nginx():
        print(f"Nginx URL: {app_url}")

        if check_application_status(app_url):
            print("Nginx is accessible from the browser.")

        else:
            print("Nginx is not accessible. Restarting application...")

            if restart_application():

                print("Checking Nginx again...")

                if check_application_status(app_url):
                    print("Nginx is accessible after restart.")
                else:
                    print("Nginx is still not accessible after restart.")

            else:
                print("Could not restart Nginx.")