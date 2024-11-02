#!/bin/bash

#SBATCH --time=6:30:00
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=2g

#SBATCH --job-name=crawling
#SBATCH --output=slurm_log/%j.out

module load eth_proxy

export APPTAINER_CACHEDIR="$SCRATCH/.singularity"
export APPTAINER_TMPDIR="${TMPDIR:-/tmp}"

# Go to the current folder
SCRIPTDIR=$(scontrol show job "$SLURM_JOB_ID" | awk -F= '/Command=/{print $2}')
SCRIPTDIR=$(realpath "$SCRIPTDIR")
cd $(dirname "$SCRIPTDIR")

# # source /users/pkoludarov/miniconda3_x86/etc/profile.d/conda.sh
# source /cluster/home/$USER/miniconda3/etc/profile.d/conda.sh
# conda activate venv

make apptainer-up
