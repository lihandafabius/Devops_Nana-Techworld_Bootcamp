#!/bin/bash

# Accept log directory parameter
if [ -z "$1" ]
then
    echo "Usage: $0 <log_directory>"
    exit 1
fi

LOG_DIRECTORY=$1

if [ ! -d "$LOG_DIRECTORY" ]
then
    echo "Log directory does not exist. Creating it..."
    mkdir -p "$LOG_DIRECTORY"
fi

LOG_DIRECTORY=$(realpath "$LOG_DIRECTORY")
export LOG_DIR=$LOG_DIRECTORY

echo "LOG_DIR set to $LOG_DIR"

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

SERVICE_USER="myapp"

# Check if user exists
if id "$SERVICE_USER" >/dev/null 2>&1
then
    echo "Service user $SERVICE_USER already exists."
else
    echo "Creating service user $SERVICE_USER..."
    sudo useradd -m -s /bin/bash $SERVICE_USER
fi


# Download artifact
echo "Downloading artifact..."
wget https://node-envvars-artifact.s3.eu-west-2.amazonaws.com/bootcamp-node-envvars-project-1.0.0.tgz

# Extract artifact
echo "Extracting artifact..."
tar -xvzf bootcamp-node-envvars-project-1.0.0.tgz 

# Give ownership to service user
sudo chown -R $SERVICE_USER:$SERVICE_USER $(pwd)
sudo chown -R $SERVICE_USER:$SERVICE_USER $LOG_DIR

# Set environment variables
export APP_ENV=dev
export DB_USER=myuser
export DB_PWD=mysecret
export LOG_DIR="$LOG_DIRECTORY"

echo "Environment variables set."


# Create application directory
sudo mkdir -p /opt/myapp

# Move extracted files
sudo mv package/* /opt/myapp/

# Give ownership to service user
sudo chown -R $SERVICE_USER:$SERVICE_USER /opt/myapp

# Change into app directory
cd /opt/myapp || exit

# Install dependencies
echo "Running npm install..."
sudo -u $SERVICE_USER npm install

# Run app with service user in background
echo "Starting Node app in background..."
sudo -u $SERVICE_USER APP_ENV=dev DB_USER=myuser DB_PWD=mysecret LOG_DIR="$LOG_DIRECTORY" npm start &

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
	
