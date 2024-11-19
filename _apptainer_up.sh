#!/bin/bash

# Path configurations
SINGULARITY_DEF="deployments/Singularity"
REQUIREMENTS="requirements.txt"
BUILD_TRIGGER="deployments/.apptainer_build_trigger"
BUILD_TRIGGER_NEW="deployments/.apptainer_build_trigger.new"
BUILT_IMAGE="deployments/_temp.built_image.sif"
FORCE_REBUILD="deployments/.force_rebuild"

# Generate new checksums
sha256sum $SINGULARITY_DEF $REQUIREMENTS > $BUILD_TRIGGER_NEW

# Check for changes or force rebuild flag
if [ ! -f "$BUILT_IMAGE" ] || ! cmp -s "$BUILD_TRIGGER" "$BUILD_TRIGGER_NEW" || [ -f "$FORCE_REBUILD" ]; then
    echo "Rebuilding Apptainer image..."
    apptainer build --fakeroot --force $BUILT_IMAGE $SINGULARITY_DEF
    mv $BUILD_TRIGGER_NEW $BUILD_TRIGGER
    rm -f $FORCE_REBUILD
else
    echo "No rebuild needed."
    rm $BUILD_TRIGGER_NEW
fi

# Run the container
TIMESTAMP=$(date +%Y-%m-%dT%H.%M.%S.%6N)
LOGFILE=$(mktemp -u .XXXXXXXX).log
apptainer run --bind ./:/app --pwd /app $BUILT_IMAGE > $LOGFILE 2>&1 &
PID=$!
PGID=$(ps -o pgid= -p $PID | tr -d ' ')  # Get the process group ID, remove spaces
echo "Container started with GID $PGID, logging to $TIMESTAMP.log"

# Move log file after the container starts
mv $LOGFILE "$TIMESTAMP.log"

# Implement a timer to stop the process after 3 hours
sleep 10800
kill -- -$PGID  # Send SIGTERM to all processes in the group
echo "Apptainer processes have been stopped after 3 hours."

