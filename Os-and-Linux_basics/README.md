# TechWorld with Nana – DevOps Bootcamp  
## Module 1: OS & Linux Basics – Bash & Application Deployment Exercises

This repository folder contains my solutions to the Linux and Bash scripting exercises from **TechWorld with Nana DevOps Bootcamp**.

The exercises focus on:

- Linux fundamentals
- Bash scripting
- User & process management
- Package installation
- Environment variables
- Running Node.js applications
- File permissions
- Service user configuration

To find the answers and implementations, refer to the corresponding script files in this repository.

---

# 📘 Exercises Overview

---

## 🧪 EXERCISE 1: Linux Mint Virtual Machine

Create a Linux Mint Virtual Machine and investigate the system configuration.

Tasks completed:

- Verified Linux distribution
- Identified package manager (`apt`, `apt-get`)
- Checked configured CLI editor (Nano, Vim, etc.)
- Identified default shell for user(bin/bash)
- Identified software center / software manager

This exercise helped understand:
- Linux distributions
- Package management systems
- Shell configuration
- Default system tools

---

## ☕ EXERCISE 2: Bash Script – Install Java

Write a Bash script (created using Vim) that:

1. Installs the latest Java version
2. Verifies installation using `java -version`
3. Checks three conditions:
   - Java is not installed
   - Java version is lower than 11
   - Java version is 11 or higher

The script prints appropriate messages for each condition.

Key concepts practiced:
- Conditional statements (`if`)
- Command substitution
- Parsing command output using `awk`
- Version validation logic

---

## 🔎 EXERCISE 3: Bash Script – User Processes

Write a Bash script that:

- Checks all running processes for the current user (`$USER`)
- Prints them to the console

Tools used:
- `ps aux`
- `grep`
- Environment variables

This exercise reinforced:
- Process inspection
- Filtering command output
- Working with environment variables

---

## 📊 EXERCISE 4: Bash Script – User Processes Sorted

Extend previous script to:

- Ask user input for sorting preference:
  - By CPU usage
  - By Memory usage
- Print sorted process list

Concepts practiced:
- User input handling (`read`)
- Sorting with `sort`
- Conditional logic

---

## 🔢 EXERCISE 5: Bash Script – Number of User Processes Sorted

Further extend script to:

- Ask how many processes to display
- Use `head` to limit output

Concepts practiced:
- Command piping
- Output limiting
- Combining multiple CLI utilities

---

# 🚀 NodeJS Application Deployment Exercises

Context: A ready NodeJS application that reads environment variables needs to run on a server.

---

## 📦 EXERCISE 6: Bash Script – Start Node App

Write a script that:

- Installs NodeJS and NPM
- Prints installed versions
- Downloads application artifact (.tgz)
- Extracts the artifact
- Sets required environment variables:
  - `APP_ENV=dev`
  - `DB_USER=myuser`
  - `DB_PWD=mysecret`
- Runs:
  - `npm install`
  - `node server.js`
- Runs the app in background

Concepts practiced:
- Package installation
- Background processes (`&`)
- Environment variables
- Artifact handling
- Basic deployment workflow

---

## 🩺 EXERCISE 7: Bash Script – Node App Check Status

Extend script to:

- Check if application is running
- Capture PID
- Print process details
- Detect and display listening port

Tools used:
- `ps`
- `ss`
- PID handling

Concepts practiced:
- Process validation
- Service health checks
- Port inspection

---

## 📝 EXERCISE 8: Bash Script – Node App with Log Directory

Extend script to:

- Accept a `log_directory` parameter
- Create directory if it doesn’t exist
- Set `LOG_DIR` environment variable
- Ensure application writes logs to provided directory
- Verify `app.log` file creation

Concepts practiced:
- Parameter handling (`$1`)
- Directory validation
- Absolute paths (`realpath`)
- File permissions

---

## 👤 EXERCISE 9: Bash Script – Node App with Service User

Final extension:

- Create dedicated service user: `myapp`
- Run application using:
  **sudo -u myapp**
- Ensure proper file and directory ownership
- Resolve permission and environment variable scope issues

Concepts practiced:
- Linux user management
- `useradd`
- `chown`
- Running applications as non-root user
- Security best practices

---

# 🧠 Key Learning Outcomes

By completing these exercises, I gained hands-on experience with:

- Linux distributions and system configuration
- Bash scripting fundamentals
- Process management
- File and directory permissions
- Environment variable handling
- Running services as non-root users
- Debugging real-world permission and path issues
- Structuring application directories properly
- `/opt/myapp`
- `/var/log/myapp`

---

# ▶️ How to Run

Each exercise script can be executed with:

```bash
chmod +x script-name.sh
./script-name.sh
./node_app_with_service_user.sh  /var/log/myapp
