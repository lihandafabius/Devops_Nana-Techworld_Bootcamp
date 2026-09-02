import boto3

ec2_client = boto3.client('ec2', region_name='eu-north-1')

response = ec2_client.describe_subnets()

for subnet in response['Subnets']:
    print(subnet['SubnetId'])