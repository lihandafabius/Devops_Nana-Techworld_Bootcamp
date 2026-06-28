##### Deploy autoscaling component

The YAML file template used in the lecture can be found here - https://raw.githubusercontent.com/kubernetes/autoscaler/master/cluster-autoscaler/cloudprovider/aws/examples/cluster-autoscaler-autodiscover.yaml

##### Updated autoscaling configuration
Addition to ServiceAccount 

```
annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam:ACCOUNTID:role/EKSServiceAccountRole
```
Additions to Deployment
```
cluster-autoscaler.kubernetes.io/safe-to-evict: "false"
env:
    - name: AWS_REGION
      value: "YOUR_AWS_REGION"
- —node-group-auto-discovery=asg:tag=k8s.io/cluster-autoscaler/enabled,k8s.io/cluster-autoscaler/NAME-OF-CLUSTER
- —balance-similar-node-groups
- —skip-nodes-with-system-pods=false
image: registry.k8s.io/autoscaling/cluster-autoscaler:v1.XX.X
```

##### Deploy nginx pods with service
```
kubectl apply -f nginx.yaml
```