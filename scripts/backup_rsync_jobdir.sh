#!/bin/bash

# Resolve the directory this script lives in, regardless of where it is called from
BASE_DIR=$(dirname "$(dirname "$(readlink -f "$0")")")
JOBDIR="$BASE_DIR/app/adminch_crawler/persistence/jobdir"
BACKUP_DIR="$BASE_DIR/data/backup_persistence/scrapy_jobs"
MAX_BACKUPS=10
# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Timestamp for backup naming
TIMESTAMP=$(date +%Y%m%d%H%M%S)
BACKUP_PATH="$BACKUP_DIR/jobdir_backup_$TIMESTAMP"

# Ensure directory exists for rsync
mkdir -p "$BACKUP_PATH"

# Sync JOBDIR to backup location using rsync
rsync -av --delete "$JOBDIR/" "$BACKUP_PATH/"

# Remove old backups, keeping only the last $MAX_BACKUPS
cd "$BACKUP_DIR"
ls -dt jobdir_backup_* | tail -n +$((MAX_BACKUPS+1)) | xargs rm -rf




# # #!/bin/bash

# # # Configuration
# # DEFAULT_JOBDIR="/path/to/default/scrapy/project/JOBDIR"  # Default path, used if the environment variable is not set
# # JOBDIR="${SCRAPY_JOBDIR:-$DEFAULT_JOBDIR}"  # Use SCRAPY_JOBDIR if set, otherwise use default
# # BACKUP_DIR="../data/backup/scrapy_jobs"
# # MAX_BACKUPS=10

# # # Create backup directory if it doesn't exist
# # mkdir -p "$BACKUP_DIR"

# # # Timestamp for backup naming
# # TIMESTAMP=$(date +%Y%m%d%H%M%S)
# # BACKUP_PATH="$BACKUP_DIR/jobdir_backup_$TIMESTAMP"

# # # Ensure directory exists for rsync
# # mkdir -p "$BACKUP_PATH"

# # # Sync JOBDIR to backup location using rsync
# # rsync -av --delete "$JOBDIR/" "$BACKUP_PATH/"

# # # Remove old backups, keeping only the last $MAX_BACKUPS
# # cd "$BACKUP_DIR"
# # ls -dt jobdir_backup_* | tail -n +$((MAX_BACKUPS+1)) | xargs rm -rf
