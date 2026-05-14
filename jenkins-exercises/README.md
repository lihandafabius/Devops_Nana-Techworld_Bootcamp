#### This project is for the DevOps bootcamp exercise for

#### "Build Automation with Jenkins"

##### Test
The project uses jest library for tests. (see "test" script in package.json)
There is 1 test (server.test.js) in the project that checks whether the main index.html file exists in the project. 

To run the nodejs test:

    npm run test

Make sure to download jest library before running test, otherwise jest command defined in package.json won't be found.

    npm install

In order to see failing test, remove index.html or rename it and run tests.


# **DOCUMENTATION**

# 🚀 CI/CD Automation with Jenkins

This project demonstrates how to build a complete CI/CD pipeline for a NodeJS application using Jenkins.

The pipeline automates:

* application versioning
* testing
* Docker image creation
* image publishing to Docker Hub
* Git operations
* deployment workflows

Additionally, the project introduces Jenkins Shared Libraries to make pipeline logic reusable across multiple projects, simulating real-world DevOps engineering practices.

The exercises cover:

* Dockerizing a NodeJS application
* Building Jenkins pipelines
* Automating version management
* Running automated tests
* Building & pushing Docker images
* GitHub webhook integration
* Avoiding CI/CD trigger loops
* Deploying updated containers
* Creating reusable Jenkins Shared Libraries

---

<details>
<summary>Exercise 1: Dockerize the NodeJS Application</summary>

<br />

The NodeJS application was containerized to ensure consistent execution across environments and simplify deployment.

### Dockerfile

```dockerfile

FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# change ownership to node user
RUN chown -R node:node /app

# switch to non-root user
USER node

EXPOSE 3000

CMD ["node", "server.js"]

```

### Key Concepts:

* **Docker layer caching optimization:**`package.json` and `package-lock.json` are copied separately before the rest of the application source code. This allows Docker to cache the dependency installation layer and avoid reinstalling dependencies every time application code changes, significantly speeding up rebuilds.
* **Lightweight base image:** Used the Alpine variant of Node.js to reduce image size and minimize the container attack surface.
* **Non-root container execution:** The application runs using the built-in `node` user instead of the root user, following container security best practices and reducing potential security risks.

After building the Docker image, the container was run locally to verify that the application started successfully and was accessible through the exposed port.

![NodeJS Docker Application](nodejs-docker-app.png)

</details>

---

<details>
<summary>Exercise 2: Create a Full CI/CD Pipeline for the NodeJS Application</summary>

<br />

A complete Jenkins pipeline was created to automate the application's build and release workflow.

### Jenkinsfile

```groovy
pipeline {
    agent any

    tools {
        nodejs 'node'
    }

    stages {

        stage('Check commit message') {
            steps {
                script {

                    def commitMessage = sh(
                        script: "git log -1 --pretty=%B",
                        returnStdout: true
                    ).trim()

                    if (commitMessage.contains('[skip ci]')) {
                        currentBuild.result = 'NOT_BUILT'
                        error('Skipping build triggered by Jenkins commit')
                    }
                }
            }
        }

        stage('Increment app version') {
            steps {
                script {

                    dir("jenkins-exercises/app") {

                        echo 'Incrementing app version'

                        sh 'npm version minor --no-git-tag-version'

                        def packageJson = readJSON file: 'package.json'
                        def version = packageJson.version

                        env.IMAGE_NAME = "${version}-${BUILD_NUMBER}"
                    }
                }
            }
        }

        stage('Test code') {
            steps {
                script {

                    echo 'Running tests'

                    sh 'cd jenkins-exercises/app && npm install && npm run test'
                }
            }
        }

        stage('Build docker image') {
            steps {
                script {

                    echo 'Building docker image'

                    withCredentials([
                        usernamePassword(
                            credentialsId: 'docker-hub-credentials',
                            usernameVariable: 'USER',
                            passwordVariable: 'PASS'
                        )
                    ]) {

                        sh "cd jenkins-exercises/app && docker build -t lihanda/demo-app:${IMAGE_NAME} ."

                        sh "echo $PASS | docker login -u $USER --password-stdin"

                        sh "docker push lihanda/demo-app:${IMAGE_NAME}"
                    }
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    echo 'Deploying application ...'
                }
            }
        }

        stage('Commit version update') {
            steps {
                script {

                    withCredentials([
                        usernamePassword(
                            credentialsId: 'github-credentials',
                            usernameVariable: 'USER',
                            passwordVariable: 'PASS'
                        )
                    ]) {

                        sh 'git config --global user.email "jenkins@example.com"'
                        sh 'git config --global user.name "jenkins"'

                        sh "git remote set-url origin https://${USER}:${PASS}@github.com/lihandafabius/Devops_Nana-Techworld_Bootcamp.git"

                        sh 'git add .'

                        sh 'git commit -m "ci: version bump [skip ci]"'

                        sh 'git push origin HEAD:main'
                    }
                }
            }
        }
    }
}
```

### Increment Version

The application version was automatically incremented using npm:

```bash
npm version minor --no-git-tag-version
```

The `--no-git-tag-version` flag prevents npm from automatically creating Git tags or commits.

### Run Automated Tests

Tests were executed before building the image to ensure only working code gets deployed.

```bash
npm install && npm run test
```

If tests fail:

* the pipeline aborts
* no Docker image is built
* no deployment occurs

### Build & Push Docker Image

The pipeline automatically:

* builds the Docker image
* tags it using the application version and Jenkins build number
* pushes it to Docker Hub

Example image tag:

```bash
lihanda/demo-app:1.4.0-32
```

### Git Integration

After incrementing the application version:

* Jenkins commits the updated `package.json`
* pushes the changes back to GitHub

### Preventing Infinite Webhook Loops

Since Jenkins pushes commits back to GitHub, GitHub webhooks can continuously retrigger the pipeline as shown below.

![Webhook loop](webhooksj.png)

To avoid this:

* Jenkins commits include `[skip ci]`
* the pipeline checks the latest commit message before continuing

### Commit Check Logic

```groovy
def commitMessage = sh(
    script: "git log -1 --pretty=%B",
    returnStdout: true
).trim()

if (commitMessage.contains('[skip ci]')) {
    currentBuild.result = 'NOT_BUILT'
    error('Skipping build triggered by Jenkins commit')
}
```

> Note: In Multibranch Pipelines, this problem can also be handled more cleanly using plugins such as **Ignore Committer Strategy**, which prevents builds triggered by commits from specific users (e.g., the Jenkins service account).

</details>

---

<details>
<summary>Exercise 3: Manually Deploy Updated Docker Image on Remote Server</summary>

<br />

After the Jenkins pipeline successfully pushed the updated Docker image to Docker Hub, the application was manually updated on the remote server.

### Steps:

* Logged into the remote server
* Pulled the latest Docker image
* Started a new container using the updated image

![Container running](dockerj.png)

* Accessed the application from the browser.

![Browser container running](browser.png)


</details>

---

<details>
<summary>Exercise 4: Extract Pipeline Logic into a Jenkins Shared Library</summary>

<br />

To improve pipeline reusability and reduce duplicated code, some pipeline logic was extracted into a Jenkins Shared Library with parameters.

This allows multiple projects to reuse common CI/CD functionality.


### Steps:

* Created a separate Git repository for the shared library at [Jenkins Shared Library](https://github.com/lihandafabius/Jenkins-shared-library.git)
* Added reusable Groovy scripts `buildDockerImage.groovy` and `commitCheck.groovyunder` inside the `vars/` folder:

### Build Docker Image Script

```groovy
#!/usr/bin/env

def call(String imageName) {
    echo 'Building docker image'
    withCredentials([usernamePassword(credentialsId: 'docker-hub-credentials', usernameVariable: 'USER', passwordVariable: 'PASS')]) {
        sh "cd jenkins-exercises/app/ && docker build -t $imageName ."
        sh "echo $PASS | docker login -u $USER --password-stdin"
        sh "docker push $imageName"
    }
}
```

### Commit Check Script

```groovy
#!/usr/bin/env

def call() {
    def commitMessage = sh(
            script: "git log -1 --pretty=%B",
            returnStdout: true
    ).trim()

    echo 'Commit message: ${commitMessage}'

    if (commitMessage.contains('[skip ci]')) {
        currentBuild.result = 'NOT_BUILT'
        error('Skipping build triggered by Jenkins commit')
    }
}
```

### Commit Version Update Script

```groovy
#!/usr/bin/env

def call() {
    withCredentials([usernamePassword(credentialsId: 'github-credentials', usernameVariable: 'USER', passwordVariable: 'PASS')]) {
        sh '''
            git config --global user.email "jenkins@example.com"
            git config --global user.name "jenkins"

            git remote set-url origin https://${USER}:${PASS}@github.com/lihandafabius/Devops_Nana-Techworld_Bootcamp.git

            git add .
            git commit -m "ci: version bump [skip ci]" || true

            git pull --rebase origin main

            git push origin HEAD:main
        '''
    }
}

```

### Jenkins Configuration

The shared library was configured globally in Jenkins:

![Jenkins-shared-lib configuration](shared-lib.png)

### Jenkins-shared-library Jenkinsfile

```groovy
#!/usr/bin/env

@Library('Jenkins-shared-library')_

pipeline {
    agent any
    tools {
        nodejs 'node'
    }

    stages {
        stage('Check commit message') {
            steps {
                script {
                    commitCheck()
                }
            }
        }
        stage('Increment app version') {
            steps {
                script {
                    incrementAppVersion()
                }
            }
        }
        stage('Test code') {
            steps {
                script {
                    echo 'Running test'
                    sh 'cd jenkins-exercises/app && npm install && npm run test'
                }
            }
        }
        stage('Build docker image') {
            steps {
                script {
                    buildDockerImage 'lihanda/demo-app:${IMAGE_NAME}'
                }
            }
        }
        stage('Deploy') {
            steps {
                script {
                    echo 'Deploying the application ..'
                }
            }
        }
        stage('Commit version update') {
            steps {
                script {
                    commitVersionUpdate()
                }
            }
        }
    }

}
```

</details>

---

## Challenges & Fixes

### 1. GitHub Webhook Infinite Trigger Loop

* **Issue:** Jenkins pushed version bump commits back to GitHub, which continuously retriggered the webhook

* **Fix:**

  * Added `[skip ci]` to Jenkins-generated commits
  * Added commit message validation stage at the beginning of the pipeline
