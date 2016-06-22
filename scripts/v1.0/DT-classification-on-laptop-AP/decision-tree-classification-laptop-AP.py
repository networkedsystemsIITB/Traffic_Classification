#------------------------Laptop-AP-Decision tree approach with complete rules and using 8 features--------------------------------------
'''This scripts  does real-time classification of the flows and prioritization/de-prioritization in Laptop-AP setup.

Here we have used following 8 features:
	1. Number of packets with push flag set,
	2. Avg window size
	3. Avg Packet Size
	4. Std. deviation of packet size	
	5. Avg. IAT(ms)
    6. Std. daviation of IAT(ms)
	7. Total Bytes
	8. Flow duration

It uses pcapy module to capture the live traffic and process each packet one by one.
'''
import socket
from struct import *
import datetime,time
import pcapy
import sys,math
import subprocess,os
#--------------------------------------
minPacket = 1000 				#Minimum number of packets after which we classify the flow (Threshold point).   
src_port = ""					
dst_port = ""
main_packet_size = {}    		# dictionary to store list of packet sizes for each flow (Here key = flowID, value = list of packet sizes)
flow_list = [] 					# contains the flowIDs (a combination of SIP,DIP,srcPort, dstPort)                 
main_inter_arrival_time = {}    # dictionary to store list of IATs for each flow (Here key = flowID, value = list of IATs)
last_time={}					# for each flow we store timestamp of the last packet arrival 
window_sizes = {}	 			# for each flow, it stores sum of windows sizes 
push_flags = {}      			# for each flow, it stores total count of push flags which are 'SET'
string={}						# For each flow, we have a string of feature values (just for printing purpose, on screen)

#####count = 0						

length = 0 						# Number of packets in a flow
avg_pkt_size = 0				# average packet size of a flow
std_dev_pkt_size = 0			# standard deviation of packet sizes in a flow
avg_iat = 0						# average IAT of a flow
std_dev_IAT = 0					# standard deviation of IAT in a flow
pktsize = 0						# packet size
win_size = 0					# Advertized window size
total_bytes = 0					# total bytes in a flow
flow_duration = 0				# Total flow duration


var_pkt_size = 0				# variance of packet sizes of a flow

rule1 = ""						# used to execute iptables rule
rule2 = ""						# used to execute iptables rule

proto = ""						# whether a packet/flow is UDP or TCP
start_time  = time.time() 		# initial time

tag = "" 						#tag given by decision tree method

def main(argv):
	dev = "wlan0"										# interface on which packet will be captured

	cap = pcapy.open_live(dev , 100 , 1 , 1000) 		# Here, open_live() captures packet
														# 1st parameter : interface name
														# 2nd parameter : How many bytes to capture in each packet
														# 3rd parameter : promiscous mode
														# 4th parameter : Read timeout time
	
	#start sniffing packets, infinite while loop
	while(1) :
		(header, packet) = cap.next() 					# capture packets, one by one
		parse_packet(packet)							# parse each packet

#Convert a string of 6 characters of ethernet address into a dash separated hex string
def eth_addr (a) :
	b = "%.2x:%.2x:%.2x:%.2x:%.2x:%.2x" % (ord(a[0]) , ord(a[1]) , ord(a[2]), ord(a[3]), ord(a[4]) , ord(a[5]))
	return b


#function to parse a packet
def parse_packet(packet) :
	#parse ethernet header
	eth_length = 14
	eth_header = packet[:eth_length] 					# upto  header
	eth = unpack('!6s6sH' , eth_header)					# un-packing 
	eth_protocol = socket.ntohs(eth[2])

	#Parse IP packets, IP Protocol number = 8
	if eth_protocol == 8 :								# checks if it is an IP packet
		#Parse IP header
		ip_header = packet[eth_length:20+eth_length]	# take first 20 characters for the ip header
		
		#now unpack them :)
		iph = unpack('!BBHHHBBH4s4s' , ip_header)
		pktsize =  int(iph[2])
		
		version_ihl = iph[0]
		version = version_ihl >> 4
		ihl = version_ihl & 0xF

		iph_length = ihl * 4							


		protocol = iph[6]								# protocol (TCP/UDP)
		s_addr = socket.inet_ntoa(iph[8]);				# source IP address
		d_addr = socket.inet_ntoa(iph[9]);				# destination IP address

		time1  = time.time() - start_time 				# How many seconds have elapsed since this script started, works as unique timestamp for packets
		
		#TCP protocol
		if protocol == 6 :								# protocol 6 referes to TCP protocol
			proto = "tcp"
			if("172.16.1" in str(d_addr)):				# Client machines had 172.16.1.XX ips, so we are interested in only those packets coming to these IPs
				if(pktsize > 1500):						# if packet size is more than 1500, set it to 1500  
					pktsize = 1500
			
			t = iph_length + eth_length
			tcp_header = packet[t:t+20]				
			tcph = unpack('!HHLLBBHHH' , tcp_header)
			tcph_v2 = unpack('!HHLLHHHH' , tcp_header)  # sp, dp, Seq, ack, first2B (16 bits), winSize
			src_port = tcph[0]							# source port
			dst_port = tcph[1]							# destination port
			
				#sequence = tcph[2]   						# L, not used
            #acknowledgement = tcph[3]      			# L, not used
            #doff_reserved = tcph[4]					# not used
            #tcph_length = doff_reserved >> 4			# not used
			

			# To identify each flow uniquely, we concatenate SIP,DIP,SP,DP to make the key
			key  = str(s_addr)+"|"+ str(d_addr)+"|"+str(src_port)+"|"+str(dst_port)
			
			first16bits = tcph_v2[4]
			push_flag_str = first16bits & 0x0008		# push flag in string format
			push_flag = int(push_flag_str)/8			# push flag in 0/1 form
			
			win_size_str = tcph_v2[5]					
			win_size = int(win_size_str)				# advertized window size in integer

			
			if (key in flow_list):													# check if the packet belongs to already existing flow ? 
				main_packet_size[key].append(pktsize)								# if YES, append its packet size to the packet size list for this flow
				lasttime = last_time[key]											
				diff = round(float(time1) - float(lasttime),8) 						# calculate inter-arrival time (seconds)
				main_inter_arrival_time[key].append(diff) 							# append IAT
				window_sizes[key] = window_sizes[key] + win_size					# update the sum of window size for the flow
				if(push_flag == 1):													# check if the PSH flag is set, and update the count if 1
					push_flags[key] = push_flags[key] + 1
				last_time[key] = time1												# update last time for the flow, to the timestamp of this packet

				
			else:																	# if this packet is the first one in this NEW flow
				flow_list.append(key)												# make its entry in the existing flow List
				main_packet_size[key] = [pktsize]									# make its entry in the packet size dictionary
				main_inter_arrival_time[key] = []									# create a blank list in this disctionary, as it is the first packet
				window_sizes[key] = win_size										# Initialize its entry for window size dictionary
				if(push_flag == 1):													# initilize push count for this new flow
					push_flags[key] = 1																	
				else:
					push_flags[key] = 0

				last_time[key] = time1												

			#sys.stdout.write(str(time1)+"|"+str(s_addr)+"|"+ str(d_addr)+"|"+str(src_port) + "|" + str(dst_port)+"|"+pktsize )

			if (len(main_packet_size[key]) == 200 and ("172.16.1" not in str(s_addr)) and ("10.42." not in str(s_addr))):									# This is to just print on screen that 200 packets have arrived in this flow
				print key, "200 packets arrived so far......."	
			if (len(main_packet_size[key]) == 750 and ("172.16.1" not in str(s_addr)) and ("10.42." not in str(s_addr))):									# This is to just print on screen that 750 packets have arrived in this flow
				print key, "-------------750 packets arrived so far......."

			if (len(main_packet_size[key]) == int(minPacket)):			# flow has reached Threshold point, Now call the function to calculate features and then classify the flow
				if(("172.16.1" not in str(s_addr)) and ("10.42." not in str(s_addr))):  					# ignore ACK packets going from 172.16.1.XX ip address, as we are interested in 				
					calculate(key,proto)								# classifying only incoming packets flows
																					
						


# This function takes two parameters as input, 1. flowID, 2. protocol
# It calculates the features values, and then checks if they pass the decision tree rules
# if they pass, it further prioritize the flow using Iptables rules
def calculate(key,proto) :
	feature_vector = " "
	
	packet_list = main_packet_size[key]									# packet_list contains the list of packet sizes for the flow in consideration	
	length=len(packet_list)												# number of packets
	total_bytes = int(sum(packet_list)) 								# Total_bytes in the flow
	avg_pkt_size = total_bytes/length									
	summ = 0	
	for j in packet_list:												# calculating standard deviation of packet sizes
		summ = summ + (avg_pkt_size - j)*(avg_pkt_size - j)
	var_pkt_size = summ/length											# variance of packet sizes
	std_dev_pkt_size = int(math.sqrt(var_pkt_size))						
	feature_vector ="  Avg pkt size:"+str(avg_pkt_size)+" Pkt_size_Std_Dev : "+str(std_dev_pkt_size)+"   Total_Bytes : "+str(total_bytes)		# concatenate features in string format

		
	inter_arrival_time_list = main_inter_arrival_time[key]				# a list containing IATs for the flow
	length = len(inter_arrival_time_list)							    
	if (length > 0):
		flow_duration = sum(inter_arrival_time_list)					# flow duration
		avg_iat = 1000*1.0*flow_duration/length							# averag IAT in miliSeconds
		summ=0
		for iat in inter_arrival_time_list:
			iat = 1000.0*iat 											# covert each IAT to ms, and then calculate 
			summ=summ + (iat-avg_iat)*(iat-avg_iat) #ms
		
		std_dev_IAT = round(math.sqrt(1.0*summ/(length)),2)   			# standard deviation of IATs
	
	
		feature_vector = feature_vector+"		AVG_IAT : "+str(round(float(avg_iat),2))+"		IAT_Std_Dev :"+str(std_dev_IAT)                            #concatenate

	avg_win_size = window_sizes[key]/len(main_packet_size[key])   		# average window size
	feature_vector = feature_vector + "    Avg_win_size = " + str(avg_win_size) + "   PSH_count = "+str(push_flags[key])
	
	# At this point , we have all the features calculated us, so we need to check the if else conditions to see if this flow belongs to multimedia
	# These if-else rules are generated by decision tree classifier(BFTree) on weka

	tag = 'download'   												# default tag assigned as 'Download'

	if(avg_win_size<31380.5):
		if(avg_iat<3.3):
			if(total_bytes< 1497085.5):
				tag='multimedia'				
			elif(avg_win_size<8792.5):		
				tag='multimedia'				


		elif(avg_iat>=3.3):
			if(push_flags[key]<279):
				if(total_bytes<1495564.5):
					if(push_flags[key]<88.5):
						tag='multimedia'			
					elif(avg_iat<7.625 and avg_iat>=4.23):
						if(avg_pkt_size < 1453):
							tag='multimedia'    	

			elif(push_flags[key]>=279):
				if(push_flags[key]<312.5):
					if(avg_pkt_size<1346):
						tag='multimedia'			
					if(avg_pkt_size>=1346):
						if(push_flags[key] >= 308):
							tag='multimedia'		

	elif(avg_win_size>=31380.5):
		if(avg_win_size<33132.5):
			if(push_flags[key]>=378.5):				
				tag='multimedia'
		elif(avg_win_size>=33132.5):		
			if(push_flags[key]>=7.5):
				if(push_flags[key]<44.5):
					if(avg_iat<6.035):
						tag='multimedia'			
				else: 															# psh_flags >= 44.5
					if(push_flags[key]<256):	
						if(avg_win_size >=35025.5 and avg_win_size <40510.5):  
							tag='multimedia'	
					else: 													    # psh_flags >= 256
						tag='multimedia'

	# By this we have the tag, decided by the above if-else rules
	print 'Decision tree TAG =', tag
	
	# if the flow is tagged as Multimedia, we need to priritize it, and for that we need to fetch the SIP, DIP, SP, DP from the key
	# and then apply the iptables rules accordingly, to put the flow in high priority band
	tuples = key.split("|")
	sip = tuples[0] 										  # source ip
	dip = tuples[1] 										  # dst ip
	sp = tuples[2] 											  # source port
	dp = tuples[3]  										  # dst port

	if( tag == 'multimedia'): 
		print  "KEY : "+key+"------" ,tag,"------" ,feature_vector      # print on the screen
		
		# There are three bands, band 5 : priritized,   band 6 : neutral,   band 7 : de-prioritized
		# iptables rule1 make sure that any packet coming from 'sip' with port 'sp', and going to 'dip' and port 'dp' get marked as '5'. 
		# iptables rule2 does the same, but for all packets flowing in the reverse direction 
		rule1 = "sudo iptables -A POSTROUTING -t mangle -d "+dip+" -s "+sip+" -p "+proto+ " --dport "+dp+"  --sport "+sp+" -j MARK --set-mark 5 "
		rule2 = "sudo iptables -A POSTROUTING -t mangle -s "+dip+" -d "+sip+" -p "+proto+ " --sport "+dp+" --dport "+sp+" -j MARK --set-mark 5 "
		
		# execute these two rules now
		subprocess.call(rule1, shell=True)     
		subprocess.call(rule2, shell=True)

		print "iptables Rules for multimedia flows, got executed......."
	else:
		# download flow 									
		print  "KEY : "+key+"------",tag,"------",feature_vector   #when it could not qualify the rule..print with ******
		# mark these packets as 7, as band 7 is de-prioritized band.
		rule1 = "sudo iptables -A POSTROUTING -t mangle -d "+dip+" -s "+sip+" -p "+proto+ " --dport "+dp+"  --sport "+sp+" -j MARK --set-mark 7 "
		rule2 = "sudo iptables -A POSTROUTING -t mangle -s "+dip+" -d "+sip+" -p "+proto+ " --sport "+dp+" --dport "+sp+" -j MARK --set-mark 7 "
		
		# execute these two rules now
		subprocess.call(rule1, shell=True)     
		subprocess.call(rule2, shell=True)

		print "iptables Rules for Download flows, got executed......."		

if __name__ == "__main__":
  main(sys.argv)
