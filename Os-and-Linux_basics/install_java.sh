#!/bin/bash

# check if java exists
if java -version >/dev/null 2>&1
then 
	echo "java is already installed."
else
	echo "java is not installed."
	echo "installing latest java... "
	sudo apt update
	sudo apt install -y default-jdk
fi

# validate java installation
if ! java -version >/dev/null 2>&1
then
	echo "java installation failed"
	exit 1
fi

# Get Java version
version=$(java -version 2>&1 | awk -F '"' '/version/ {print $2}')
major_version=$(echo $version | awk -F '.' '{print $1}')

echo "Detected Java version: $version"

# Check conditions
if [ "$major_version" -lt 11 ]
then
    echo "Older Java version detected (less than 11)."
else
    echo "Java 11 or higher is installed."
    echo "Installation successful!"
fi
