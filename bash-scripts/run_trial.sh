#!/bin/sh
#SBATCH --cpus-per-task=1
#SBATCH --mem=5gb
#SBATCH --time=96:00:00

#SBATCH --job-name=ifwaste
#SBATCH --mail-type=END
#SBATCH --output=logging_2k.out

date 
module load python 
module load mamba 
mamba activate ifwaste-env

date
python /home/haasehelen/haasehelen/ifwaste/model/main.py --config_path /home/haasehelen/haasehelen/ifwaste/bash-scripts/experiments/config_trial.json
date 
