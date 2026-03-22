#!/bin/bash

NEXUS_USER=""
NEXUS_PASS=""
NEXUS_URL="http://<server ip>:8081"
REPO="npm-repository"
APP_NAME="bootcamp-node-project"

# 1. Fetch latest version info
DOWNLOAD_URL=$(curl -s -u "$NEXUS_USER:$NEXUS_PASS" \
     "$NEXUS_URL/service/rest/v1/search?repository=$REPO&name=$APP_NAME" \
     | jq -r '.items[0].assets[0].downloadUrl')

# 2. Download artifact
curl -u "$NEXUS_USER:$NEXUS_PASS" -L -o "$APP_NAME.tgz" "$DOWNLOAD_URL"

# 3. Extract
rm -rf "$APP_NAME"
tar -xvzf "$APP_NAME.tgz" 

# 4. Run app in background
cd "package"
sudo apt install npm
npm install
nohup node server.js > app.log 2>&1 &

echo "Application started!"
