#!/bin/bash
# Count number of runs
iterations=10

# List of scenarios - adjust to your scenario name
scenarios=(
    "scenario0_no_promotions"
    "scenario1_bogos_only"
    "scenario2_sales_only"
    "scenario3_both"
)

# Loop through scenarios and submit job arrays
for scen in "${scenarios[@]}"; do
    echo "Submitting jobs for $scen ..."
    sbatch --array=0-${iterations} run_1_nh_all_hh_n_times.sh "$scen"
done
