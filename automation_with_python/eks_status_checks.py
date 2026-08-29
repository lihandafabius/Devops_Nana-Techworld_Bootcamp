import boto3

eks_client = boto3.client('eks', region_name='eu-north-1')
clusters = eks_client.list_clusters()['clusters']

for cluster in clusters:
    response = eks_client.describe_cluster(
        name=cluster
    )
    cluster_status = response['cluster']['status']
    cluster_endpoint = response['cluster']['endpoint']
    cluster_version = response['cluster']['version']
    print(f"Cluster {cluster} is {cluster_status}, running kubernetes version {cluster_version} and available at: {cluster_endpoint}")

