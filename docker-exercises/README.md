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

### Key Concepts:

* Sensitive values (e.g., DB credentials) should **not be hardcoded**
* Environment variables allow **flexible configuration across environments**
* Improves **security and portability**

</details>

---

<details>
<summary>Exercise 1: Start MySQL Container </summary>
<br />

Instead of installing MySQL locally, I used Docker to quickly spin up a database container.

### Steps:

* Pulled the official MySQL image
* Started the container with required environment variables:

  * `MYSQL_ROOT_PASSWORD`
  * `MYSQL_DATABASE`
  * `MYSQL_USER`
  * `MYSQL_PASSWORD`
* Exposed port `3306`
* Verified database connectivity from the application

</details>

---

<details>
<summary>Exercise 2: Start phpMyAdmin Container </summary>
<br />

To visualize and manage database data, I deployed a UI tool.

### Steps:

* Started container using phpMyAdmin
* Configured connection to MySQL container
* Accessed via browser and successfully logged in

</details>

---

<details>
<summary>Exercise 3: Docker Compose for MySQL & phpMyAdmin </summary>
<br />

To simplify container management, I introduced Docker Compose.

### Steps:

* Created a `docker-compose.yaml` file
* Defined both MySQL and phpMyAdmin services
* Configured:

  * Shared network
  * Persistent volume for database (`mysql-data`)
* Verified both services start together

</details>

---

<details>
<summary>Exercise 4: Dockerizing the Java Application </summary>
<br />

The Java application was containerized to run alongside other services.

### Steps:

* Created a `Dockerfile` for the application
* Built the application JAR using Gradle
* Packaged the application into a Docker image
* Verified container runs successfully

</details>

---

<details>
<summary>Exercise 5: Build & Push Docker Image to Nexus </summary>
<br />

To enable remote deployment, the application image was stored in a private registry.

### Steps:

* Created a **Docker hosted repository** in Sonatype Nexus Repository Manager
* Built Docker image locally
* Tagged image with Nexus repository address
* Pushed image to Nexus
* Verified image availability in Nexus UI

</details>

---

<details>
<summary>Exercise 6: Add Application to Docker Compose </summary>
<br />

The application was integrated into the Compose setup.

### Steps:

* Added Java app service to `docker-compose.yaml`
* Configured environment variables for DB connection
* Implemented MySQL health check:

```yaml
healthcheck:
  test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
  interval: 10s
  timeout: 5s
  retries: 5
```

* Used `depends_on` with `service_healthy` condition

### Result:

* Ensured correct startup order (DB → App)

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

