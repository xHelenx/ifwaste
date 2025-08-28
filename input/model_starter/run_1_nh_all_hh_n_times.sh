#!/bin/sh
#SBATCH --cpus-per-task=1
#SBATCH --mem=8gb
#SBATCH --time=30:00:00
#SBATCH --job-name=ifwaste
#SBATCH --mail-user=<YOUR-EMAIL>
#SBATCH --mail-type=END,FAIL
#SBATCH --output=../../output/slurm_logs/slurm_output_%A_%a.out

module load mamba
mamba activate ifwaste-env

# Scenario name comes from argument
scenario_name=$1
path="../gsua_based_configuration/samples/shopping/${scenario_name}/"

nh_id=0
hh_id=all

echo "Running scenario: $scenario_name"
echo "Path: $path"

nh_id=0
hh_id=all

echo "Setting up simulation with 1 neighborhood config and all household samples"
echo "Using samples in: $path"
echo Starting experiment: ${SLURM_ARRAY_TASK_ID}
echo "Submitting jobs for $scen ..."
python ../../model/main.py --full_csv --agg_csv --path $path --nh_id $nh_id --hh_id $hh_id --sim_run_id ${SLURM_ARRAY_TASK_ID} 

