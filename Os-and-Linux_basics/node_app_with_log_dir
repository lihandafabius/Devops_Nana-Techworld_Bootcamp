#!/bin/bash

# check if installed or not
if node -v >/dev/null 2>&1 && npm -v >/dev/null 2>&1
then
    echo "NodeJS and NPM already installed."
else
    echo "Installing NodeJS and NPM..."
    sudo apt update
    sudo apt install -y nodejs npm
fi

# Validate installation
if ! node -v >/dev/null 2>&1 || ! npm -v >/dev/null 2>&1
then
    echo "NodeJS and NPM installation failed."
    exit 1
fi

# Print versions
echo "Node version: $(node -v)"
echo "NPM version: $(npm -v)"

# Download artifact
echo "Downloading artifact..."
wget https://node-envvars-artifact.s3.eu-west-2.amazonaws.com/bootcamp-node-envvars-project-1.0.0.tgz

# Extract artifact
echo "Extracting artifact..."
tar -xvzf bootcamp-node-envvars-project-1.0.0.tgz

# Set environment variables
export APP_ENV=dev
export DB_USER=myuser
export DB_PWD=mysecret

echo "Environment variables set."

# Change into project directory
cd package || exit

# Install dependencies
echo "Running npm install..."
npm install

# Run app in background
echo "Starting Node app in background..."
node server.js > app.log 2>&1 &

# Get Pid of the last backround process
PID=$!

# Allow sometime for the app to start
sleep 2

# Check if process is running
if ps -p $PID > /dev/null
then
	echo "Application started successfully."
	echo "Process ID: $PID"

	echo "Process details"
	ps -fp $PID

	# Check listening port
	PORT=$(ss -tulnp 2>/dev/null | grep $PID | awk '{print $5}' | cut -d: -f2)
       	if [ -n "$PORT" ]
        then
       		echo "Application is listening on port: $PORT"
        else
        	echo "Application is running but no listening port detected."
	fi
else
	echo "Appication process is not running"
fi
	
