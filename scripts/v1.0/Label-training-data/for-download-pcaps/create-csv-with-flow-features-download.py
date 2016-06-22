'''
 This script is invoked by create-training-for-download.sh
 It takes 2 inputs:
	1. file as input which contains many rows, each row represents a packet's information. This scripts associates each packet to a flow (4-tuple. SIP,DIP,SP,DP).
	2. number of packets after which we will classify the flow (i.e. 1000) 
	
Finally it calculates 8 features for each flow and outputs the same in a csv file.

 8 features:
	1. Number of packets with push flag set,
	2. Avg window size
	3. Avg Packet Size
	4. Std. deviation of packet size	
	5. Avg. IAT(ms)
    6. Std. daviation of IAT(ms)
	7. Total Bytes
	8. Flow duration

'''

import math
import sys
filename = sys.argv[1]  		#name of .txt file, containing time, sip,dip,sp,dp,pktSize etc

main_packet_size = {}    		# dictionary to store list of packet sizes for each flow (Here key = flowID, value = list of packet sizes)
flow_list = [] 					# contains the flowIDs (a combination of SIP,DIP,srcPort, dstPort)                 
main_inter_arrival_time = {}    # dictionary to store list of IATs for each flow (Here key = flowID, value = list of IATs)
last_time={}					# for each flow we store timestamp of the last packet arrival 

avg_pkt_sizes={}				# contains the flowID and their calculated average packet sizes
string={}						# For each flow, we have a string of feature values (just for printing purpose, on screen)

window_size = {} 				# to store the sum of window sizes of a connection
win_size = 0					# Advertized window size
packet_count = {}				# contains flowID as key and number of packets as value
push_flag_count = {}			# contains flowID as key and number of packets with PSH flag 'set' as value

#=========================================================================================================================================================
min_number_of_packets = int(sys.argv[2]) 			# if number of packets in a flow is less than this, then we ignore any such flow from our analysis
number_of_pkts_limit = int(sys.argv[2]) 			# we store info abt these many pkts in each flow, after this ignore
#=========================================================================================================================================================

# open the given txt file, read each line (each line here represents one packet), and fetch the values by spliting the line
with open(filename,'r') as f1:
	for line in f1:
		l = line.split("|")
		time = float(l[0])							# timestamp of the packet			
		dstip = l[2]								# destination IP
		srcip = l[1]								# source IP
		srcport = l[3]								# source port
		dstport = l[4]								# destination port
		pktsize = int(l[5])							# packet size
		push_flag_str = l[6]						# push flag 0 or 1
		if not push_flag_str:						# if PSH  is a NULL string , set it to 0, else convert to int
			push_flag = 0
		else:
			push_flag = int(push_flag_str)

		win_size = l[7].split('\n')[0]				# window size
		
		if not win_size:							# if window size is a NULL string , set it to 0, else convert to int
			win_size = 0
		else:
			win_size = int(win_size)
		

		# check if srcport or dstport is null string, if yes, set it to 0
		if(srcport==''):
			srcport='0';
		
		if(dstport==''):
			dstport='0';

		# To identify each flow uniquely, we concatenate SIP,DIP,SP,DP to make the key
		key = srcip +'	'+ dstip +'	'+ srcport +'	'+ dstport
		
		if (key in flow_list) :													# check if the packet belongs to already existing flow ? 
			if (len(main_packet_size[key]) < number_of_pkts_limit ):			# check if, less that specified limit of packets
				packet_count[key] = packet_count[key] + 1						# increament packet count
				main_packet_size[key].append(pktsize)							# append its packet size to the packet size list for this flow
				lasttime = last_time[key]
				diff = round(float(time) - float(lasttime),8)					# calculate inter-arrival time (seconds)
				main_inter_arrival_time[key].append(diff)						# append IAT

				if(push_flag==1):												# check if the PSH flag is set, and update the count if 1
					push_flag_count[key] = push_flag_count[key]+1				
				window_size[key] = window_size[key] + win_size 					# update the sum of window size for the flow
				last_time[key] = time											# update last time for the flow, to the timestamp of this packet

				
		else:																	# if this packet is the first one in this NEW flow
			flow_list.append(key)												# make its entry in the existing flow List
			packet_count[key] = 1												# first packet arrived for this flow, set count =1			
			main_packet_size[key] = [pktsize]									# make its entry in the packet size dictionary
			main_inter_arrival_time[key] = []									# create a blank list in this disctionary, as it is the first packet
			if(push_flag==1):													# initilize push count for this new flow
				push_flag_count[key] = 1
			else:
				push_flag_count[key] = 0 

			window_size[key] = win_size 										# Initialize its entry for window size dictionary, next time keep on adding to it
			last_time[key] = time	

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
for key in main_packet_size.keys():
    packet_list = main_packet_size[key]											# packet_list contains the list of packet sizes for the flow in consideration	
    length=len(packet_list)														# number of packets
    avg_pkt_sizes[key] = sum(packet_list)/length								# calculate avg packet size, and store													    
    summ = 0																	# Now calculate variance and standard deviation of packet sizes
    for j in packet_list:
    	summ = summ + (avg_pkt_sizes[key] - j)*(avg_pkt_sizes[key] - j)
    var_pkt_size = summ/length
    std_dev_pkt_size = int(math.sqrt(var_pkt_size))
    string[key]=key+","+str(avg_pkt_sizes[key])+","+str(std_dev_pkt_size)+","+str(sum(packet_list))+","+str(len(packet_list))    # concatenate features in string format
#------------------- ---------------------------------------------------------------------------------------------------------------------------------------------------

# Now calculate average IAT, standars deviation of IAT
for key in main_inter_arrival_time.keys():
	inter_arrival_time_list = main_inter_arrival_time[key]						# a list containing IATs for the flow
	length=len(inter_arrival_time_list)
	if length > 0:
		flow_duration = sum(inter_arrival_time_list)							# flow duration
		avg_iat = flow_duration/length       									# Average IAT
		avg_iat_in_ms = round(1000*avg_iat,2)									# convert in millisecond

		summ=0  
    	for iat in inter_arrival_time_list:
    		summ=summ + (iat-avg_iat)*(iat-avg_iat) 
		std_dev_IAT = round(1000*math.sqrt(summ/(length)),6)					# standard deviation of IATs in ms

		# we consider a flow only if at least 'min_number_of_packets' in that flow and average packet size > 800, as we want to avoid noisy/unwanted flows
        if(len(main_packet_size[key]) >= min_number_of_packets and  avg_pkt_sizes[key] > 800 ):      
        	string[key]=string[key]+","+str(avg_iat_in_ms)+","+str(std_dev_IAT)+","\
        	+str(flow_duration)+","+str(push_flag_count[key])+","+str(window_size[key]/len(main_packet_size[key]))+","+"Download" 
        	print string[key]

# Here string[key] contains the feature vector in string format with the 4-tuple(SIP,DIP,SP,DP) appended in front

#=================================================================================END=========================================================================================


