#!/bin/bash

user_name=`whoami` #(your_user_name)
weka_path=/home/$user_name/weka-3-6-13/weka.jar



# This script is used to generate KNN model from the training file which must be in CSV format.

# Below line converts the training file (data.csv) in to arff format.
sudo java -Xmx2024m -classpath CLASSPATH:$weka_path weka.core.converters.CSVLoader data.csv > train-data.arff

# Next line builds the model using training data set and save it as knn.model
sudo java -Xmx2024m -classpath CLASSPATH:$weka_path weka.classifiers.lazy.IBk -K 1 -W 0 -A "weka.core.neighboursearch.LinearNNSearch -A \"weka.core.EuclideanDistance -R first-last\""  -t train-data.arff -d knn.model >a



