# IFWASTE project
The model includes household agents that purchase groceries from the store and store them, cook with ingredients and eat meals. During this process different waste types are being produced and monitored, analyzed and visualized.

![test](img/concept_overview.PNG)


## Table of contents
- [IFWASTE project](#ifwaste-project)
  - [Table of contents](#table-of-contents)
  - [Version overview](#version-overview)
  - [Requirements](#requirements)
  - [Installation and setup](#installation-and-setup)
  - [Running the model](#running-the-model)
  - [Parameterizing the simulation](#parameterizing-the-simulation)
  - [Project Information](#project-information)


## Version overview 

| Model version |Features                                                                                                                                                                                                                                              | Link                                                        |
|---------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------|
| v0            | - random shopping<br>- cooking with random items<br>- eating food by calories<br>- basic storage managment                                                                                                                                            | https://github.com/oriley531/IFWASTE                        |
| v1            | additional to v0<br>- serving based consumption<br>- storage is queryable by different factors<br>- plate waste and leftover handling<br>- quick shopping <br>- quick cooking <br>- level of concern<br>- tracking more information during simulation | https://github.com/xHelenx/ifwaste/tree/first_model_version |

## Requirements 
The project is the developed in Python 3.12.5. 

We use *pip* as a package manager that allows you to install, manage, and uninstall Python packages and their dependencies.

You can install python [here](https://www.python.org/downloads/). Ensure
that you are using at least version 3.12.5. 

*Pip* is available to download [here](https://pypi.org/project/pip/). 

## Installation and setup
1. You can download the code from GitHub either by 
clicking on the green *Code* button on the top right SELECT THE RIGHT VERSION and then by clicking on *Download ZIP* or if you are using git 
you can clone the repository

        git clone https://github.com/xHelenx/ifwaste.git

1. We are using a *Makefile* to create a virtual environment and then installs the required libaries. A virtual environment ensures that when you install libraries for a python project they are only used within this environment. That way you can have multiple setups for different projects without them conflicting one another. In order to run the script you have to open a console and navigate to the downloaded ifwaste folder. In Windows click on the search bar on the bottom left on your screen, type in *Command prompt* and open the console. Navigate to your folder by using `cd \enter\path\to\ifwaste\folder`
3. Run the following command to run the script. On Windows
    
        make venv

    On macOS use: 

        make venvMac

4. Now activate the virtual environment. On a windows machine use: 
   
        .\venv\Scripts\activate

    On macOS use: 

        source venv/bin/activate
## Running the model 
Now you are ready to run the model. In order to do so you can either open an IDE and execute the project or open the console again and navigate to the ifwaste-path. 
From there run the following 

    cd model/
    python main.py 


After the simulation finished you should find a new folder called `data` in your project. In this folder you can find a folder your simulation name. It includes the generated .csv files that can be used for further analysis. 


## Parameterizing the simulation 
After running the default version you can also change the configuration to your own 
wishes: 


The current simulation run is configure in the `config.json` file. This file includes information about the `Simulation` itself, including how many times to run the experiment (runs), how many days the simulation should collect data from (total_days) and what the name of the output file should be (name). 

Furthermore the `Neighborhood` can be configured, by including the number of houses (neighborhood_houses, neighborhood_serving_based). The House can have a number of children and adults (hh_amount_children,hh_amount_adults). Each person type (Adult and Child) has a range of the ratio of how man plate waste (0-1) they produce (adult_plate_waste_min, adult_plate_waste_max,child_plate_waste_min,child_plate_waste_max)

You can adapt these values accordingly. 

If you want to change the values of lower lever parameters, open `globals.py`. The following table gives an overview of the parameters and their meanings. 


| **Parameter** | **Description** | **Value** |
|:----------------------------:|-----------------------------------------------------------------------------------------|:------------------:|
| EXPIRATION\_THRESHOLD        | expiry threshold causing a family, that eats by expiry date to use this ingredient first | 4                  |
| MIN\_TIME\_TO\_COOK          | minimal required time to be able to cook                                                 | 0.8 (48min)        |
| SERVINGS\_PER\_GRAB          | portion in servings of an ingredient that is taken when choosing ingredients for a meal  | 8                  |
| KCAL\_PER\_GRAB              | portion in kcal of an ingredient that is taken when choosing ingredients for a meal      | 100                |
| INGREDIENTS\_PER\_QUICKCOOK  | number of ingredients used for a quickcook                                               | 2                  |
| MAX\_SCALER\_COOKING\_AMOUNT | maximal multiplier for how much more food to cook, 1 is for one day                      | 3                  |
| SERVING\_SIZES               | portion sizes that are can be purchased at the store                                     | [6,12,20]          |
| ADULT\_AGE\_MIN              | minimal considered adult age                                                             | 18                 |
| ADULT\_AGE\_MAX              | maximal considered adult age                                                             | 65                 |
| ADULT\_CONCERN\_MIN          | minimal concern value for eating expiring food, range 0-1                                | 0.3                |
| ADULT\_CONCERN\_MAX          | maximal concern value for eating expiring food, range 0-1                                | 0.7                |
| CHILD\_CONCERN\_MIN          | minimal concern value for eating expiring food, range 0-1                                | 0                  |
| CHILD\_CONCERN\_MAX          | maximal concern value for eating expiring food, range 0-1                                | 0.3                |

The level of concern can also be directly edited in `House.py` by changing the variable value of `self.household_concern` to a value between 0 and 1. 

## Project Information
The project is supported by the Foundation for Food and Agriculture Research as well as the Kroger Zero Hunger Zero Waste Foundation. 