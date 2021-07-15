"""
The purpose of this script is to run collect data on the performance of
SEE-Classify applied to the dataset used in Dhahri et al. 2019.
This script will generate a CSV file, where each line contains the following information:

<trial-number>,<generation-number>,<best-hof-fitness>

The default parameters for the Genetic Algorithm are
Population Size (--pop-size) = 10
Number of Generations (--num-gen) = 10
Number of Trials (--num-trials) = 100
"""

import argparse
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import make_moons, make_circles, make_classification
from see import GeneticSearch
from see.base_classes import pipedata
from see.classifiers import Classifier
from see.classifier_fitness import ClassifierFitness
from see.classifier_helpers import helpers
from see.Workflow import workflow

parser = argparse.ArgumentParser(description="Create some csv data files.")

parser.add_argument(
    "--num-gen",
    default=10,
    type=int,
    help="number of generations to run genetic search (default: 20)",
)

parser.add_argument(
    "--pop-size",
    default=10,
    type=int,
    help="population size of each generation to run genetic search (default: 20)",
)

parser.add_argument(
    "--num-trials",
    default=100,
    type=int,
    help="number of trials to run genetic search (default: 100)",
)

args = parser.parse_args()

## PRINT MESSAGE

## WAIT MESSAGE...

# Initialize Algorithm Space and Workflow
algorithm_space = Classifier.algorithmspace

workflow.addalgos([Classifier, ClassifierFitness])
wf = workflow()

# Create Data:

## Read Breast Cancer Data
url = "https://archive.ics.uci.edu/ml/machine-learning-databases/breast-cancer-wisconsin/wdbc.data"
data = pd.read_csv(url, header=None)

X = data.iloc[:, 2:].to_numpy()


def diagnosis_to_category(d):
    if d == "M":
        return 0
    elif d == "B":
        return 1
    else:
        print("WARNING: UNKNOWN Category")


# Turn classifications Malignant(M)/Benign(B) into binary (0/1) assignments
y = np.vectorize(diagnosis_to_category)(data[1].to_numpy())

# Preprocess data
X = StandardScaler().fit_transform(X)

# Feature Selection
# src: https://scikit-learn.org/stable/auto_examples/compose/plot_feature_union.html
from sklearn.pipeline import FeatureUnion
from sklearn.decomposition import PCA

# Table 1 suggests using 12 components for GAs
#pca = PCA(n_components=12, svd_solver='randomized')
pca = PCA(n_components=12)
#print("Using auto svd_solver in PCA")

# Use feature union in case we want to combine multiple feature selections later
combined_features = FeatureUnion([("pca", pca)])

# Use combined features to transform dataset:
X_features = combined_features.fit(X, y).transform(X)
#X_features = X

# Split data into training and testing sets and
# create a dataset object that can be fed into the pipeline
# A train-test-valid split of 60-20-20
temp = helpers.generate_train_test_set(X_features, y, test_size=0.2)
validation_set = temp.testing_set
pipeline_dataset = helpers.generate_train_test_set(temp.training_set.X, temp.training_set.y, test_size=0.25, random_state=900)
print('Pipeline random_state = 900')

NUM_GENERATIONS = args.num_gen
NUM_TRIALS = args.num_trials
POP_SIZE = args.pop_size

# TODO...use cross-validation...because the paper uses cross-validation...
print("Running {} Dataset".format("Dhahri 2019"))
print("GA running for {} generations with population size of {}".format(NUM_GENERATIONS, POP_SIZE))
print("Size of dataset: {}".format(len(X)))
print("Size of training set: {}".format(len(pipeline_dataset.training_set.X)))
print("Size of testing set: {}".format(len(pipeline_dataset.testing_set.X)))
print("Size of validation set: {}".format(len(validation_set.X)))

for i in range(NUM_TRIALS):
    print("Running trial number {}".format(i))
    my_evolver = GeneticSearch.Evolver(workflow, pipeline_dataset, pop_size=POP_SIZE)
    my_evolver.run(
        ngen=NUM_GENERATIONS,
	print_raw_data=True
    )
