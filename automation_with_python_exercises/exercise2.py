import boto3
from operator import itemgetter

iam = boto3.client('iam')

paginator = iam.get_paginator('list_users')
for response in paginator.paginate():
    users = response['Users']
    for user in users:
        print(f"User: {user['UserName']}")
        print(f"Last Time Active: {user['PasswordLastUsed']}")

    sorted_users = sorted(users, key=itemgetter('PasswordLastUsed'), reverse=True)
    recent_user = sorted_users[0]
    print(f"Recent User is : {recent_user['UserName']} with the id : {recent_user['UserId']}")