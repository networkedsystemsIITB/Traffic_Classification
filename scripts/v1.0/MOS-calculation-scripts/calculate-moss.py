
# This sccript calculates MOS score using latency, jitter and loss percentage parameters.

# This script takes two input :  total number of lost packets and total packets


import math
import sys
import numpy

flow_list = []   										# this list contains all the RTT

with open('a.txt','r') as f1:
	for line in f1:
		time = float(line)
		if (time < 5):    								# we ignores long RTT packets those are outliers  
			flow_list.append(time)
			

count=0
summ=0
a=0
avg_RTT=0
rtt_dif=0                 
avg_diff=0
last=0

#--------------------------------------------------------------------------------------------------------------------------------

for key in flow_list:
	summ=summ+key 											# summ represents sum of RTTs
	count=count+1											# count represents total number of packets
	if(a==1):
		rtt_dif=rtt_dif+abs(key-last)						# rtt_diff represents jitter, which is difference between the two consecutive RTTs
	a=1
	last=key

if(count>0):
	avg_RTT=summ/count   		     						#  average RTT 
	avg_diff=rtt_dif/(count-1)								#  average jitter


avg_RTT=avg_RTT*1000										# convert it to milli seconds
avg_diff=avg_diff*1000										# convert it to milli seconds


loss_per=float(sys.argv[1])*100/float(sys.argv[2])          # calculate loss percentage


print "Avg latency:	"+ str(avg_RTT) +" ms"						
print "Avg jitter:	"+ str(avg_diff) +" ms"						
print "Lost percentage:	"+str(loss_per)+" %"						

'''
We use the following equations from Pingplotter software page ( https://www.pingman.com/kb/article/how-is-mos-calculated-in-pingplotter-pro-50.html ) to calculate the MOS score
=========================================================================================

' Take the average latency, add jitter, but double the impact to latency
' then add 10 for protocol latencies
EffectiveLatency = ( AverageLatency + Jitter * 2 + 10 )

' Implement a basic curve - deduct 4 for the R value at 160ms of latency
' (round trip).  Anything over that gets a much more agressive deduction
if EffectiveLatency < 160 then
   R = 93.2 - (EffectiveLatency / 40)
else
   R = 93.2 - (EffectiveLatency - 120) / 10

' Now, let's deduct 2.5 R values per percentage of packet loss
R = R - (PacketLoss * 2.5)

' Convert the R into an MOS value.(this is a known formula)
MOS = 1 + (0.035) * R + (.000007) * R * (R-60) * (100-R)
=========================================================================================
'''

r=0
el=0 														# effective latency
el=avg_RTT+avg_diff*2+10
if(el<160):
	r=93.2-(el/40)	
else:
	r=93.2-(el-120)/10

mos=0

r = r - (loss_per * 2.5)

mos= 1 + (0.035) * r + (.000007) * r * (r-60) * (100-r)   # calculate the MOS score 


print "MOS Score:	"+str(mos)



