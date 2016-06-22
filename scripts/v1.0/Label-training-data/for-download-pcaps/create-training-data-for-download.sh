# This is the main script...
# This script is meant for fetching download flows from the trace file given.
# This script finally generates a csv file containing 4-tuple(SIP,DIP,SP,DP) along with 8 feature values for that flow. Each row in that csv represents a unique flow.

# As we use this script to fetch download flows, and they are further used to train the classifier. The traces we took on different machines and we were only interested in all incoming packets. So we set filters to identify incoming packets. In our case, the client machines had following IPs.
client_ip34="172.16.1.34"
client_ip12="172.16.1.12"
client_ip13="172.16.1.13"

# Delete temporary files which are not needed,
# Here we have used *csv, *txt which will delete all txt and csv files, so be CAREFUL.
rm -rf *csv *.txt

# Here we want to run this script on all the trace files (pcap files) present in the current directory.
# keep all the training pcap files in the current folder before running this script.


# following loop, takes each pcap file one by one and on each pcap file, we apply a filter to find all packets which are incoming to any one of the mentined ip addresses.
# it creates a txt file named as pcapFileName.txt, which has many rows, each row re presents a packet.

# for each pcap file, we have one txt file generated here

# Now this txt file is given to another script 'create-csv-with-flow-features-download.py' , which will convert this packet level information to flow level information
# That script will generate a csv file which will contain download flows along with 4-tuple information and feature values


for f in *.pcap
do
	echo $f
	tshark -r $f  -R "(ip.dst==$client_ip34 or ip.dst==$client_ip12 or ip.dst==$client_ip13)" -T fields -e frame.time_relative -e ip.src -e ip.dst -e tcp.srcport -e tcp.dstport -e ip.len -e tcp.flags.push -e tcp.window_size -E separator='|' > $f.txt

done



# Next 'create-header.py' will generate a csv file containing only one row .i.e. Header, that will be used when we merge all CSV files into one file
python create-header.py > aaa_Header.csv				# this filename must come first in alphabetical order, this is needed for successfully merging the csv files
														# that's why dummy aaa appended in the name, in the front.


#Now run python script to generate csv file, where Each row will represents a download flow.
for f in *.txt
do
	python create-csv-with-flow-features-download.py $f 1000 > $f.csv   # 1st param:txt file ; 2nd param : threshold points (no. of packets after which classification need to be done)

done
rm -rf all-download-flows.csv
cat *.csv > all-download-flows.csv

# at this point of time, we have created 'all-download-flows.csv' which contains all the download flows along with their feature values.
# Now just put all temporary txt and csv file to a new directory txt-files and CSV-files respectively.
rm aaa_Header.csv				# not required, delete it
mkdir -p CSV-files				# create directory if not exist already
mkdir -p txt-files


mv *txt txt-files/
mv *csv CSV-files

mv CSV-files/all-download-flows.csv .
