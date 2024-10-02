#!/bin/sh
#SBATCH --cpus-per-task=1
#SBATCH --mem=5gb
#SBATCH --time=96:00:00
#SBATCH --job-name=ifwaste_array
#SBATCH --mail-type=END
#SBATCH --output=run_array_log_%A_%a.out
#SBATCH --array=0-3

date
module load python
module load mamba
mamba activate ifwaste-env

# Map array index to config files
CONFIG_FILES=("experiments/config_0k.json" "experiments/config_2k.json" "experiments/config_4k.json" "experiments/config_6k.json")
CONFIG_PATH=${CONFIG_FILES[$SLURM_ARRAY_TASK_ID]}

echo "Running Experiment $SLURM_ARRAY_TASK_ID"

date
python main.py --config_path $CONFIG_PATH
date

