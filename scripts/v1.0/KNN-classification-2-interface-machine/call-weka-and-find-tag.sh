#!/bin/bash

user_name=`whoami` #(your_user_name)
weka_path=/home/$user_name/weka-3-6-13/weka.jar

# This weka_path

# This script is invoked by 'knn-classification-script.py' after features values have been calculated for the flow in the consideration.
# It uses the training data (train-data.arff) and the KNN model (knn.model) to predict the class tag for the test flow (test-data.arff).

# Below line converts the training file (data.csv) in to arff format.
#sudo java -Xmx2024m -classpath CLASSPATH:$weka_path weka.core.converters.CSVLoader data.csv > train-data.arff

# Next line builds the model using training data set and save it
#sudo java -Xmx2024m -classpath CLASSPATH:$weka_path weka.classifiers.lazy.IBk -K 1 -W 0 -A "weka.core.neighboursearch.LinearNNSearch -A \"weka.core.EuclideanDistance -R first-last\""  -t train-data.arff -d knn.model >a

# we have commented above commands to convert the data in csv file to arff file, and also the command which creates the model using that training data in arff format, as these two things we need to do only when there is any update in the training data.


# Now load the knn model and then classify the test data

# This command will use the existing knn model, train data and test instance to predict the tag
java -Xmx2024m -classpath CLASSPATH:$weka_path weka.classifiers.lazy.IBk   -l   knn.model -T test-data.arff | tail -4|head -3|cut -d "|" -f1>temp.txt

cat temp.txt

<<COMMENT1
contents of temp file looks like:
=== Confusion Matrix ===

  a     b     <-- classified as
  I    II   | a = download
 III   IV   | b = multimedia
============================
here only one among I,II,III,IV have 1, rest will have zeros. 
with respect to identifying multimedia class:
	case 1 : if I = 1 , it means that flow is actually download , also has been classified as Download    (True negative)
	case 2 : if II = 1 , it means that flow is actually download , BUT has been classified as Multimedia  (False positive)
	case 1 : if III = 1 , it means that flow is actually multimedia , BUT has been classified as Download (False nagative)
	case 1 : if IV = 1 , it means that flow is actually multimedia , also has been classified as Multimedia (True positive)


But here all we need to find is that what tag has been assigned to the flow. that can be found by checking which column has 1.
if column 1 has 1 (at I or III position) : then flow has been classified as Download
if column 2 has 1 (at II or IV position) : then flow has been classified as Multimedia

This is what we find out in the rest of the code...
and save the tag in tha tag.txt file.
COMMENT1

#-------------------------------------------------------------------------------------------------------------

a=`cut -d " " -f2 temp.txt|grep 1|wc -l`
if [ $a -eq 1 ];
then
echo "download" >tag.txt
exit
fi

b=`cut -d " " -f3 temp.txt|grep 1|wc -l`

if [ $b -eq 1 ];
then
echo "multimedia"  >tag.txt
exit
fi
c=`cut -d " " -f4 temp.txt|grep 1|wc -l`

rm temp.txt
#====================================================END========================================================




