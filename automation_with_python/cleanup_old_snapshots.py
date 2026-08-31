import boto3
from operator import itemgetter

ec2_client = boto3.client('ec2', region_name='eu-north-1')

volumes =ec2_client.describe_volumes(
    Filters=[
        {
            'Name': 'tag:Name',
            'Values': [
                'prod'
            ]
        },
    ]
)

for volume in volumes['Volumes']:

    snapshots = ec2_client.describe_snapshots(
        OwnerIds=['self'],
        Filters=[
            {
                'Name': 'Volume-id',
                'Values': [volume['VolumeId']]
            }
        ]
    )

sorted_by_date = sorted(snapshots['Snapshots'], key=itemgetter('StartTime'), reverse=True)

# for snap in snapshots['Snapshots']:
#     print(snap['StartTime'])
#
# print('##########################################')
#
# for snap in sorted_by_date:
#     print(snap['StartTime'])

for snap in sorted_by_date[2:]:
    response = ec2_client.delete_snapshot(
        SnapshotId=snap['SnapshotId']
    )
    print(response)


