import boto3
from operator import itemgetter

ecr_client = boto3.client('ecr')
response = ecr_client.describe_repositories()
repositories = []
for repository in response['repositories']:
    print(repository['repositoryName'])
    repositories.append(repository['repositoryName'])



repository_name = repositories[0]
images = ecr_client.describe_images(repositoryName=repositories[0])
sorted_images_by_date = sorted(images['imageDetails'], key=itemgetter('imagePushedAt'), reverse=True)
for image in sorted_images_by_date:
    tag = image.get('imageTags')
    if tag:
        print(f"Time of Push: {image['imagePushedAt']}")
        print(f"Image tag: {tag}")
        print("######################################################")

