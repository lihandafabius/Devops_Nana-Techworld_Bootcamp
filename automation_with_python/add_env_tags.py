import boto3

ec2_client_Stockholm = boto3.client('ec2', region_name ='eu-north-1')
ec2_resource_Stockholm = boto3.resource('ec2', region_name ='eu-north-1')

ec2_client_UK = boto3.client('ec2', region_name ='eu-west-2')
ec2_resource_UK = boto3.resource('ec2', region_name ='eu-west-2')

instance_ids_Stockholm = []
instance_ids_UK = []

reservations_Stockholm = ec2_client_Stockholm.describe_instances()['Reservations']
for res in reservations_Stockholm:
    instances = res['Instances']
    for instance in instances:
        instance_ids_Stockholm.append(instance['InstanceId'])


response = ec2_resource_Stockholm.create_tags(
    Resources=instance_ids_Stockholm,
    Tags=[
        {
            'Key': 'environment',
            'Value': 'prod'
        },
    ]
)

reservations_UK = ec2_client_UK.describe_instances()['Reservations']
for res in reservations_UK:
    instances = res['Instances']
    for instance in instances:
        instance_ids_UK.append(instance['InstanceId'])


response = ec2_resource_UK.create_tags(
    Resources=instance_ids_UK,
    Tags=[
        {
            'Key': 'environment',
            'Value': 'Dev'
        },
    ]
)

