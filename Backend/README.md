# Project Name Sales Sage Backend

This project is meant for the backend server where it runs both our ASR, ToDo list recommendation, Sentimental analysis. Through using Flask for api integration with our React web application.

## Installation

## Virtual environment 1 (Python 3.9)
REMEMBER TO CHANGE YOUR HF SECRET KEY IN 'run_whsiperX.py' and 'test_whisperX.py' AT THE LINE WHERE 'diarize_model' IS BEING CALLED AND SUBS TO THE REPO PROVIDED IN WHISPERX REPO FOR HF (link : https://github.com/m-bain/whisperX)

### Creating virtual environment
Ensure that ur python is linked to a python version 3.9 before running the command below
```
python -m venv venvone
venvone\Scripts\activate
```
Replace venvone with the name that your virtual environment to be called

### Setting up virtual environment to run the code
Run in your repo clone
```
mkdir uploads
mkdir model_data
pip install torch==2.0.0+cu118 torchaudio==2.0.0+cu118 -f https://download.pytorch.org/whl/torch_stable.html
pip install -r requirements.txt
git clone https://github.com/m-bain/whisperX.git
cd whisperX
pip install -e .
```

### Running the code
After accessing your virtual environment, cd into your repo clone
```
python server.py
```

## Virtual environment 2 (Python 3.7.1)
### Creating virtual environment with CONDA
```
conda create --name myenv python=3.7.1
```
```
conda activate myenv
```
Replace myenv with the desired name for your environment.
### Setting up virtual environment to run the code
Navigate to the snips-nlu folder. This is where the second flask app will be executed.
Following which run the two commands below to set up the virtual environment.
```
pip install -r requirements.txt
```
```
conda install --yes --file conda_requirements.txt
```
```
python -m snips_nlu download en
```
### Running the code
```
python App.py
```

