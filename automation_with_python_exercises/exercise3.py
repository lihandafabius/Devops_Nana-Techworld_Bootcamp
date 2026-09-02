import boto3
import paramiko

ec2_client = boto3.client('ec2', region_name='eu-north-1')

default_vpc = ec2_client.describe_vpcs(
    Filters=[
        {
            "Name": "is-default",
            "Values": ["true"]
        },
    ]
)

vpc_id = default_vpc['Vpcs'][0]['VpcId']

# Find a subnet in the default VPC
subnets = ec2_client.describe_subnets(
    Filters=[
        {
            "Name": "vpc-id",
            "Values": [vpc_id]
        }
    ]
)

subnet_id = subnets['Subnets'][0]['SubnetId']

# Create EC2 instance
response = ec2_client.run_instances(
    ImageId="ami-0aba19e56f3eaec05",
    InstanceType="t3.micro",
    MinCount=1,
    MaxCount=1,
    KeyName="myapp-key-pair",
    SubnetId=subnet_id
)

instance_id = response["Instances"][0]["InstanceId"]
ssh_username = "ubuntu"
app_url = f""
ssh_key = "path-to-key-pair.pem"

print(f"EC2 instance created: {instance_id}")

# Check Status
def check_instance_status():
    response = ec2_client.describe_instance_status(InstanceIds=[instance_id], IncludeAllInstances=True)
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


def get_server_ip():
    response = ec2_client.describe_instances(
        InstanceIds=[instance_id]
    )

    instance = response["Reservations"][0]["Instances"][0]

    server_ip = instance.get("PublicIpAddress")
    return server_ip


def install_docker():
    try:
        print("Checking EC2 Status")
        status_ok = check_instance_status()

        if status_ok:
            print("Application Status is OK")
            print("Installing Docker...")
            server_ip = get_server_ip()
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
                    sudo systemctl enable --now docker
                    """

            stdin, stdout, stderr = ssh.exec_command(command)

            exit_status = stdout.channel.recv_exit_status()

            output = stdout.read().decode()
            error = stderr.read().decode()

            ssh.close()

            print(output)

            if exit_status == 0:
                print("Docker installed successfully!")
                return True
            else:
                print("Docker installation failed!")
                print(error)
                return False

    except Exception as ex:
        print(f"Failed to install Docker: {ex}")
        return False

def start_nginx():
    try:
        print("Checking Docker Installation status")
        docker_installed = install_docker()

        if docker_installed:
