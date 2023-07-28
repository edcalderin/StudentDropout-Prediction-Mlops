# Experiment tracking

## Prepare env

```bash
pipenv install
source $(pipenv --venv)/Scripts/activate
```

## Create experiment with different features

After doing EDA and obtaining features, it is required run `create_experiment.py` script to track this experiment.
Basically, it trains a pipeline with a XGBoost model using random hyperparameters.

```bash
python preprocess.py
```
Create first test experiment
```bash
python create_experiment.py
```

## Hyperparamenter-optimization step
Once selected the best model, run this command to optimize the model using the features on which it was trained originally.
Create a new MLFlow experiment with a set of models derived from Optuna optimizer.

```bash
python optuna.py
```