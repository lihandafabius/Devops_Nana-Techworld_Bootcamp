def buildApp() {
    echo "building the application..."
    sh 'cd jenkins/java-maven-app/ && mvn package'
}
return this

def buildDockerImage() {
    echo 'Building the Docker image...'
    withCredentials([usernamePassword(credentialsId: 'docker-hub-credentials', usernameVariable: 'USER', passwordVariable: 'PASS')]) {
        sh 'cd jenkins/java-maven-app/ && docker build -t lihanda/demo-app:3.0 .'
        sh "echo $PASS | docker login -u $USER --password-stdin"
        sh 'docker push lihanda/demo-app:3.0'
    }

}
return this
def deployApp() {
    echo 'Deploying the application...'
}
return this
