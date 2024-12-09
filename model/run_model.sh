#!/bin/sh
#SBATCH --cpus-per-task=1
#SBATCH --mem=5gb
#SBATCH --time=96:00:00

#SBATCH --job-name=ifwaste
#SBATCH --mail-type=END
#SBATCH --output=run_log.out

module load mamba 
mamba activate ifwaste-env

echo "Starting experiment run" 
date
python main.py
date 
echo "Finished runs" 
