## 🐳 Docker & Containerized Application Deployment

This project demonstrates how to containerize and deploy a full-stack application using Docker and Docker Compose.
The setup includes a Java backend application, a MySQL database, and a phpMyAdmin UI, all orchestrated together and deployed on a remote server.

Additionally, the project integrates a private Docker registry using Sonatype Nexus Repository Manager to store and distribute application images, simulating real-world DevOps workflows.

The exercises cover:

* Running services using Docker containers
* Orchestrating multi-container applications with Docker Compose
* Building and pushing Docker images to a private registry
* Managing environment variables and secrets securely
* Deploying and accessing applications on a remote server

---

<details>
<summary>Exercise 0: Clone Repository & Environment Variables </summary>
<br />

For this exercise, I cloned the project repository and reviewed how environment variables are used within the application.
Also I reviewed some of the techniques I would use to handle sensitive env varaibles values like root passwords, user passwords etc.

These are some of the **techniques for handling senstive data** I considered to use:

* **Exporting variables (shell)** → quick for local testing
* **`.env` file** → simple to use (add to `.gitignore`)
* **Docker secrets** → more secure, not exposed as env variables
* **Cloud secret managers** (e.g. AWS Secrets Manager, HashiCorp Vault) → best for production

### Key Concepts:

* Sensitive values (e.g., DB credentials) should **not be hardcoded**
* Environment variables allow **flexible configuration across environments**
* Improves **security and portability**


</details>

---

<details>
<summary>Exercise 1: Start MySQL Container </summary>
<br />

I used Docker to quickly spin up a mysql database container in my local machine.

### Steps:

* Pulled the official MySQL image
* Started the container with required environment variables:

  * `MYSQL_ROOT_PASSWORD`
  * `MYSQL_DATABASE`
  * `MYSQL_USER`
  * `MYSQL_PASSWORD`
* Exposed port `3306`. I had another mysql instance locally, so I had to kill the instance with the Instance's process ID
* Verified database connectivity from the application by querying the database using mysql cli interface by use of `mysql -h 127.0.0.1 -p 3306 -u admin -p`

</details>

---

<details>
<summary>Exercise 2: Start phpMyAdmin Container </summary>
<br />

To visualize and manage MySQL database data, I deployed a UI tool as a Docker container.

### Steps:

* Started phpMyAdmin container using the official image  
* Configured connection to MySQL using `PMA_HOST`, set to the MySQL service/container name (Docker internal DNS)  
* Accessed via browser and successfully logged in using the database credentials defined in the MySQL container

</details>

---

<details>

<summary>Exercise 3: Use Docker Compose for MySQL and phpMyAdmin </summary>
<br />

Instead of starting containers manually, I used Docker Compose to manage both services together.

### Steps:

* Created a `docker-compose` file for MySQL and phpMyAdmin  
* Configured a named volume for persistent database storage  
* Used environment variables for dynamic configuration  
* Connected phpMyAdmin to MySQL using the service name (`mysql`) via `PMA_HOST`  

### mysql-compose.yaml

```yaml
services:

  mysql:
    image: mysql
    container_name: mysql
    ports:
      - "3306:3306"
    environment:
      MYSQL_ROOT_PASSWORD: rootpass
      MYSQL_DATABASE: team-member-projects
      MYSQL_USER: ${DB_USER}
      MYSQL_PASSWORD: ${DB_PWD}
    volumes:
      - mysql-data:/var/lib/mysql

  phpmyadmin:
    image: phpmyadmin
    container_name: phpmyadmin
    ports:
      - "8084:80"
    restart: always
    environment:
      PMA_HOST: mysql
    depends_on:
      - mysql

volumes:
  mysql-data:
    driver: local
```
</details>

---

<details>
<summary>Exercise 4: Dockerizing the Java Application </summary>
<br />

The Java application was containerized to run alongside MySQL and phpMyAdmin using Docker.

### Dockerfile:

```dockerfile
FROM eclipse-temurin:17-jdk-alpine

RUN mkdir -p /home/java-app

WORKDIR /home/java-app 

COPY build/libs/*.jar app.jar   

ENTRYPOINT ["java", "-jar", "app.jar"]
```

### Steps:

* Created a lightweight Docker image using a minimal base image (`alpine`)
* Built the application JAR using Gradle
* Copied the JAR into the container
* Defined the entrypoint to run the application
* Built and tested the container locally

### Key Concepts:

* **Minimal base image:** Using `alpine` reduces image size and improves security by minimizing the attack surface
* **Containerization:** Ensures the app runs consistently across environments
* **Layer caching:** Separating steps improves build efficiency

</details>

---

<details>
<summary>Exercise 5: Build & Push Docker Image to Nexus </summary>
<br />

To enable remote deployment, the application image was stored in a private Docker registry hosted on Nexus.

### Steps:

* Deployed **Sonatype Nexus Repository Manager** as a Docker container on the AWS EC2 instance

* Opened required ports (**8081** for UI, **8083** for Docker registry) in the security group

* Created a **Docker (hosted)** repository in Nexus

* Configured an HTTP connector on port **8083** for Docker access

* Created a dedicated role with full access to the Docker repository

* Created a user and assigned the role

* Built the Docker image locally

* Tagged the image with the Nexus repository endpoint

* Configured Docker daemon (`daemon.json`) to allow **insecure registry** access (HTTP)

* Logged in to the Nexus Docker registry

* Pushed the image to Nexus

* Verified the image in the Nexus UI

### Key Concepts:

* **Private registry:** Stores and manages Docker images securely
* **Access control:** Roles and users restrict who can push/pull images
* **Insecure registry (HTTP):** Required when SSL is not configured (common in dev setups)
* **Remote artifact storage:** Enables pulling images from any server

</details>


---

Here’s a clean, polished version of your **Exercise 6** section with all your key decisions explained clearly 👇

---

<details>
<summary>Exercise 6: Add Application to Docker Compose </summary>
<br />

The Java application was integrated into the multi-container setup and configured for remote deployment.

### Steps:

* Added the Java application service to `docker-compose.yaml` using the image from the private Nexus registry

  ### docker-compose.yaml

```yaml
services:
  java-app:
    image: localhost:8083/java-app:1.0
    ports:
      - "8080:8080"
    environment:
      DB_SERVER: mysql
      DB_USER: ${DB_USER}
      DB_PWD: ${DB_PWD}
      DB_NAME: team-member-projects
    depends_on:
      mysql:
        condition: service_healthy

  mysql:
    image: mysql
    container_name: mysql
    ports:
      - "3306:3306"
    environment:
      MYSQL_ROOT_PASSWORD: rootpass
      MYSQL_DATABASE: team-member-projects
      MYSQL_USER: ${DB_USER}
      MYSQL_PASSWORD: ${DB_PWD}
    volumes:
      - mysql-data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5


  phpmyadmin:
    image: phpmyadmin
    container_name: phpmyadmin
    ports:
      - "8084:80"
    restart: always
    environment:
      PMA_HOST: mysql
    depends_on:
      - mysql
volumes:
  mysql-data:
    driver: local
```

* Used `localhost:8083/java-app:1.0` as the image source since the registry is running on the **same server** as Docker
  → This avoids external network calls and allows faster, internal image pulls

* Updated `index.html` to use the **remote server’s IP address** instead of `localhost`
  → Ensures the frontend communicates correctly with the backend when accessed from a browser

* Rebuilt the Docker image and pushed the updated version to the Nexus repository

* Externalized sensitive configuration using a `.env` file:

* Secured the `.env` file with restricted permissions:

  ```bash
  chmod 600 .env
  ```

* Transferred the `docker-compose.yaml` file securely to the remote server using `scp`

* Configured environment variables in Compose using variable substitution:

  ```yaml
  DB_USER: ${DB_USER}
  DB_PWD: ${DB_PWD}
  ```

* Implemented MySQL health check to ensure proper startup order:

```yaml
healthcheck:
  test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
  interval: 10s
  timeout: 5s
  retries: 5
```

* Used `depends_on` with `service_healthy` condition to delay app startup until MySQL is ready

### Key Concepts:

* **Local registry access (`localhost`)**: Works because Nexus and Docker run on the same host
* **Environment variable externalization**: Keeps sensitive data out of version control
* **.env security**: Restricting permissions prevents unauthorized access
* **Service dependency management**: Ensures correct startup order in multi-container apps
* **Frontend-backend separation**: Requires proper host configuration when deployed remotely

</details>

---

<details>
<summary>Exercise 7: Deploy Application on Remote Server </summary>
<br />

The application stack was deployed on a cloud server.

### Steps:

* Configured Docker to allow insecure registry (HTTP Nexus)
* Logged into Nexus Docker repository
* Transferred `docker-compose.yaml` to server using `scp`
* Externalized environment variables using `.env` file
* Fixed frontend issue:

  * Replaced hardcoded `localhost` with dynamic host (`window.location.hostname`)
* Started services using:

```bash
docker compose up -d
```

</details>

---

<details>
<summary>Exercise 8: Open Ports & Access Application </summary>
<br />

To access the application externally:

### Steps:

* Opened required ports in server firewall:

  * `8080` → Java app
  * `8084` → phpMyAdmin
* Verified application access via browser

</details>

---

## ⚠️ Challenges & Fixes

### 1. ❌ MySQL container port conflict

* **Issue:** Port `3306` already in use
* **Fix:** Changed port mapping or stopped local MySQL service

---

### 2. ❌ Container not starting (exit errors)

* **Issue:** Missing or incorrect environment variables
* **Fix:** Verified and aligned variable names with application config

---

### 3. ❌ Database connection failure

* **Issue:** Wrong DB host (`localhost`)
* **Fix:** Used service name (`mysql`) inside Docker network

---

### 4. ❌ Frontend not updating / buttons not working

* **Issue:** Hardcoded `localhost` in frontend
* **Fix:** Replaced with dynamic host:

```javascript
const HOST = window.location.hostname;
```

---

### 5. ❌ Nexus Docker login issues

* **Issue:** HTTP registry blocked
* **Fix:** Configured Docker `insecure-registries`

---

### 6. ❌ Docker disk space issues

* **Issue:** “no space left on device”
* **Fix:** Increased AWS volume + extended filesystem

---

### 7. ❌ Image pull failures

* **Issue:** Network interruptions
* **Fix:** Retried pulls / cached images in Nexus

---

## 📚 Key Learnings

* **Containerization:**
  Docker allows packaging applications and dependencies into portable containers.

* **Multi-container orchestration:**
  Docker Compose simplifies managing multiple interconnected services.

* **Networking in Docker:**
  Containers communicate using service names, not `localhost`.

* **Environment variable management:**
  Externalizing configuration improves security and flexibility.

* **Private container registry:**
  Using Sonatype Nexus Repository Manager enables secure image storage and distribution.

* **Debugging skills:**
  Learned to troubleshoot:

  * Networking issues
  * Container startup failures
  * Volume and disk space problems

* **Cloud deployment:**
  Successfully deployed a multi-container application on a remote server.

* **Security practices:**
  Avoided hardcoding sensitive data and explored safer alternatives like `.env` and Docker secrets.

---

## 🚀 Final Outcome

A fully containerized application stack running on a remote server, including:

* Java backend application
* MySQL database
* phpMyAdmin UI
* Private Docker registry integration

All services are orchestrated using a single `docker-compose` file and can be deployed with one command.

---

