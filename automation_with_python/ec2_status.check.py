import boto3
import schedule

ec2_client = boto3.client('ec2', region_name ='eu-north-1')
ec2_resource = boto3.resource('ec2', region_name ='eu-north-1')

reservations = ec2_client.describe_instances()

# for reservation in reservations['Reservations']:
#     instances = reservation['Instances']
#     for instance in instances:
#         print(f"status of instance {instance['InstanceId']} is {instance['State']['Name']}")
#
#

def check_instance_status():
    statuses = ec2_client.describe_instance_status(IncludeAllInstances=True)
    for status in statuses['InstanceStatuses']:
        state = status['InstanceState']['Name']
        print(f"{status['InstanceId']} is {state} and instance status is: {status['InstanceStatus']['Status']}")
        print(f"{status['InstanceId']} is {state} and system status is: {status['SystemStatus']['Status']}")
    print('#######################\n')



schedule.every(5).seconds.do(check_instance_status)
# schedule.every().day.at("1:00")
while True:
    schedule.run_pending()