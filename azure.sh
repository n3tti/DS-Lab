#!/bin/bash

# Hardcoded server details
SERVER_USER="azureuser"
SERVER_HOST="20.82.5.165"
REMOTE_PATH="/tmp/biep"
COMMAND_TO_RUN="make start"

# Current local directory
LOCAL_PATH="$(pwd)"

# Create remote directory and copy files
echo "Connecting to server and copying files..."
ssh "$SERVER_USER@$SERVER_HOST" -i "~/.ssh/azure" "mkdir -p $REMOTE_PATH"
rsync -avz -e "ssh -i ~/.ssh/azure" --progress "$LOCAL_PATH/" "$SERVER_USER@$SERVER_HOST:$REMOTE_PATH/"

# Execute command
echo "Running command..."
ssh "$SERVER_USER@$SERVER_HOST" "cd $REMOTE_PATH && $COMMAND_TO_RUN"

echo "Done!"