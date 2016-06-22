# This script works on laptop-AP setup and creates 3 HTB bands and also throttles the bandwidth to 1500 KBps (here kbps == Kilo Bytes per second , and kbits = kilo bits)
# Band 5 is priritized band ;  Band 6 is neutral band ;  Band 7 is de-priritized band
# This is applied at wlan0 interface.

# Each band has two attributes:
#	1. rate :  it defines the Mininmum rate witch is guaranteed always.
#	2. ceil :  it defines the Maximum rate which can be achieved by this band, if available.

#---------------------------------

upperLimit=1500kbps    										# here kbps =>Kilo Bytes per second
lowerLimit=50kbps

sudo iptables -t mangle -F									# flush all rules from mangle table
sudo tc qdisc del dev wlan0 root 							# delete all qdisc at wlan0 , if any exist.
		
sudo tc qdisc add dev wlan0 root handle 1: htb default 6  	# create the htb qdisc at wlan0 interface

sudo tc class add dev wlan0 parent 1: classid 1:1 htb rate $upperLimit							# Define upper limit at the root of the HTB itself

sudo tc class add dev wlan0 parent 1:1 classid 1:5 htb rate $lowerLimit ceil $upperLimit prio 0  # Prioritized band 
sudo tc class add dev wlan0 parent 1:1 classid 1:6 htb rate $lowerLimit ceil $upperLimit prio 1  # Default class 
sudo tc class add dev wlan0 parent 1:1 classid 1:7 htb rate $lowerLimit ceil $upperLimit prio 2  # De-Prioritized band 


sudo tc filter add dev wlan0 parent 1:0 prio 1 protocol ip handle 5 fw flowid 1:5  				# Filter packets marked with 5 and send them to class 1:5
sudo tc filter add dev wlan0 parent 1:0 prio 1 protocol ip handle 7 fw flowid 1:7   				# Filter packets marked with 7 and send them to class 1:7


