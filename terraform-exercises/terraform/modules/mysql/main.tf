resource "helm_release" "mysql" {
  name             = "mysql"
  repository       = "oci://registry-1.docker.io/bitnamicharts"
  chart            = "mysql"


  values = [
    file("${path.module}/values.yaml")
  ]

  timeout = 600 // wait for 10 minutes for the release to be deployed
}