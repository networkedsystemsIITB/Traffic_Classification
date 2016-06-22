# This script is invoked by create-training-data-for-Multimedia.sh
# It takes a file as input which contains packets with HTTP GET request.
# It creates a string which looks like "tcp.dstport == 47997 or tcp.dstport == 49146 or ...." . This string is written into a filter.txt.

import csv
import sys, getopt

set_ports = set()
filter_string = ""

with open(sys.argv[1], 'rb') as csvfile:								# open the input file
	reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
	for row in reader:
		port = row[0].split("|")[3] # take 5th field					# split the line with '|', take 5th field, which is destination port number
		if  port :														# if dst port not null, add it to the set 
			set_ports.add(port)



# Now create the filter string by concatenating the dst ports.
for p in set_ports:		
	filter_string = filter_string + " tcp.dstport == "+p + " or "

with open('filter.txt', 'w') as f:										# write it into a file
    f.write(filter_string[:-3])


