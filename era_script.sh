#!/bin/bash
#SBATCH --job-name=test_python       # Job name
#SBATCH --output=python_output.txt  # Standard output log (print statements in your script will go here)
#SBATCH --error=python_error.txt    #Standard error log (error messages can be found here)
#SBATCH --partition=gpu_partition   # Partition name (Do not modify)
#SBATCH --gres=gpu:1         # Request 0, 1 or 2 GPUs
#SBATCH --time=00:02:00    # Set a time limit if you want, make sure to remove or set to 0 otherwise
#SBATCH --ntasks=1          # Number of tasks (keep at 1 unless you know what you're doing!)

# Load necessary modules
module load python/3.10  # Adjust as needed, this is the default compiler version
module load cuda/12.6   # Adjust as needed, this is the default compiler version

# Activate Conda or virtual environment (if used)
conda activate dssg_era          # For Conda environment, if you use one

# Run the Python script
python3 era_script.py
