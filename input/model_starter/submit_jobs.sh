#!/bin/bash
# Count number of runs
replications=15

# List of scenarios - adjust to your scenario name
scenarios=(
    "scenario0_none"
    "scenario1_bogo"
    "scenario3_both"
)

# Loop through scenarios and submit job arrays
for scen in "${scenarios[@]}"; do
    echo "Submitting jobs for $scen ..."
    sbatch --array=0-${replications} run_1_nh_all_hh_n_times.sh "$scen"
done
