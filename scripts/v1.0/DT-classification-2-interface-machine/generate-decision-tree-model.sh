#!/bin/bash

# This script is used to generate decision tree model from the given training data (filename must be data.csv)


user_name=`whoami` #(your_user_name)
weka_path=/home/$user_name/weka-3-6-13/weka.jar

sudo java -Xmx2024m -classpath CLASSPATH::$weka_path  weka.core.converters.CSVLoader data.csv > train-data.arff
java -Xmx2024m -classpath CLASSPATH:$weka_path weka.classifiers.trees.BFTree -S 1 -M 2 -N 5 -C 1.0 -P POSTPRUNED  -t train-data.arff 

