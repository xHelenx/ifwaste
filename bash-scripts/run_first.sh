#!/bin/sh
#SBATCH --cpus-per-task=1
#SBATCH --mem=5gb
#SBATCH --time=96:00:00

#SBATCH --job-name=ifwaste
#SBATCH --mail-type=END
#SBATCH --output=run_log.out

date 
module load python 
module load mamba 
mamba activate ifwaste-env

echo "Experiment 1: 0 kids"
date
python main.py --config_path experiments/config_0k.json
date 


echo "Experiment 2: 2 kids"
date
python main.py --config_path experiments/config_2k.json
date 


echo "Experiment 3: 4 kids"
date
python main.py --config_path experiments/config_4k.json
date 


echo "Experiment 4: 6 kids"
date
python main.py --config_path experiments/config_6k.json
date 

 
