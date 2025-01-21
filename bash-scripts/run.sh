#!/bin/sh
#SBATCH --cpus-per-task=1
#SBATCH --mem=1gb
#SBATCH --time=28:00:00

#SBATCH --job-name=test
#SBATCH --mail-user=haasehelen@ufl.edu
#SBATCH --mail-type=BEGIN,FAIL,END
#SBATCH --output=run_log.out

date 
module load mamba 
mamba activate ifwaste-env

echo "Experiment 1: 0 kids"
date
python main.py --config_path experiments/config_0k.json
date
