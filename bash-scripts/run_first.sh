echo "Experiment 2: 2 kids"
date
python /home/haasehelen/haasehelen/ifwaste/model/main.py --config_path /home/haasehelen/haasehelen/ifwaste/bash-scripts/experiments/config_2k.json
date 

echo "Experiment 3: 4 kids"
date
python /home/haasehelen/haasehelen/ifwaste/model/main.py --config_path /home/haasehelen/haasehelen/ifwaste/bash-scripts/experiments/config_4k.json
date 


echo "Experiment 4: 6 kids"
date

python /home/haasehelen/haasehelen/ifwaste/model/main.py --config_path /home/haasehelen/haasehelen/ifwaste/bash-scripts/experiments/config_6k.json
date 