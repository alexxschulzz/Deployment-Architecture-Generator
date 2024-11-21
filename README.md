# Deployment-Architecture-Generator
A configurable generator for deployment architectures.


## Install python virtual environment (venv)
Open the terminal and navigate to the top layer of this repo. 

Type in ```python -m venv .venv``` to create a new python virtual environment in this repo to install the needed libaries. A folder named ```.venv``` will appear.

Type in ```.\.venv\Scripts\activate``` to activate the python virtual environment. A green ```(.venv)``` will appear in fron of the command line. Now type in ```pip install -r requirements.txt``` to install all the libaries listed in ```requirements.txt```.

## Generate the base architecture files
Run ```base_architectureGenerator.py``` the base architecture ```.yaml``` files will appeare in ```/generatedFiles/base```.

## Generate the final/full architecture files
Run ```full_architectureGenerator.py``` the final/full architecture ```.yaml``` files will appeare in ```/generatedFiles/full```.

## Configure the generator
All configuration files are stored in the folder ```Config```. The generator is generic, so you can add new stacks, stack combinations or components. The basic structure of the ```.yaml``` configuration files must be preserved.

- To add new stacks, change: ```stackConfig.yaml```.
- To add new stack combinations, change: ```stackCombinationConfig.yaml```. Currently any stack combination must be defined manually. A generator to create new stack combinations could replace this file.
- To add new components, change: ```componentConfig.yaml```.