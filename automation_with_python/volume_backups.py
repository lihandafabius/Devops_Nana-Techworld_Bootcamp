import boto3
import schedule

ec2_client = boto3.client('ec2', region_name='eu-north-1')

volumes =ec2_client.describe_volumes(
    Filters=[
        {
            'Name': 'tag:Name',
            'Values': [
                'prod'
            ]
        },
    ],
)
def create_snapshot():
    for volume in volumes['Volumes']:
        new_snapshot = ec2_client.create_snapshot(
            VolumeId=volume['VolumeId']
        )
        print(new_snapshot)


schedule.every().day.do(create_snapshot)

while True:
    schedule.run_pending()