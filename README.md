# IFWASTE project

The model includes household agents that purchase groceries from the store and store them, cook with ingredients and eat meals. During this process different waste types are being produced and monitored, analyzed and visualized. 

![test](img/concept_overview.PNG)

## Directory Structure 

    
    📦model
    ┣ 📜Child.py
    ┣ 📜CookedFood.py
    ┣ 📜Food.py
    ┣ 📜House.py
    ┣ 📜Neighborhood.py
    ┣ 📜Person.py
    ┣ 📜Store.py
    ┣ 📜main.py
    ┣ 📜globalValues.py
    ┗ 📜Storage.py
    📦analysis
    ┣ report.Rmd
    ┣ 📂plots
    ┃ ┣ 📜bought_hh_servings.png
    ┃ ┣ 📜...
    📦data
    ┗ 📂2024-04-10at09-45
    ┃ ┣ 📜bought.csv
    ┃ ┣ 📜eaten.csv
    ┃ ┣ 📜wasted.csv
    ┃ ┣ 📜still_have.csv
    ┃ ┣ 📜daily.csv
    ┃ ┗ 📜config.csv
    ┗

 ## Requirements 
The project is developed in Python 3.9.13. 
The analysis is devleoped using R version 4.3.3, you might require extra installations to run 
the R-markdown format. 

 ## Running the project
In order to run the simulation follow these steps: 

1. Download/clone the git repository 
2. Run [main.py](model/main.py) located in the model folder

After the simulation finished you should find a new folder with the current timestamp being generated in the data folder. It includes the generated .csv files that can be used for further analysis. 

You can analyze them yourself of navigate to the [report.Rmd](analysis/report.Rmd), located in the analysis folder to generate predefined graphics. Therefore follow the next steps. 

1. Open *report.md*. 
2. Follow the instruction 0-4 in the report including: 
   1. Installing missing libraries
   2. Defining the folder path of the input path (you might have to change the / to \ if you are using Mac)
   3. Choose, whether you want to save the files directly
   4. Optionally, change the design settings 

Once you got familar with this workflow, you can also change the simulation parameters.
For now most parameter are defined directly in the class, a few have already been migrated to *globalValues.py*. 


 **TODO: move all parameters to one file.**
