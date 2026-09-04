import boto3


ecr_client = boto3.client('ecr', region_name='eu-north-1')

def fetch_images():
    allowed_tags = ["1.0", "2.0", "3.0"]

    images = ecr_client.describe_images(repositoryName="java-maven-app")

    images_digests = []

    for image in images["imageDetails"]:
        for tag in image.get("imageTags", []):
            if tag in allowed_tags:
                image_digest = image["imageDigest"]
                images_digests.append(f"{tag}|{image_digest}")


    return images_digests

if __name__ == "__main__":
    images = fetch_images()


    for image in images:
        print(image)