#This script calculate latency (rtt), jitter and loss percentage, and using it it finds MOS score for given pcap file 


# the following command gives list of RTT of all the packets, we use ip filter to remove unnecessary packets.  YOu must set ths ip as the ip of your client machines IP on which you took these trace files (pcap files)
tshark -r $1 -R "tcp.analysis.ack_rtt and (ip.dst==172.16.255.255/16 or ip.src == 172.16.255.255/16)" -e tcp.analysis.ack_rtt -T fields -E separator=, -E quote=d > n.txt

sed 's/"//g' n.txt > a.txt


# the following command calcuates tcp retransmission, number of duplicate acks, number of lost segments and number of fast retransmission
tshark -r $1 -R "(ip.dst==172.16.255.255/16 or ip.src == 172.16.255.255/16)" -q -z io,stat,10000,"COUNT(tcp.analysis.retransmission) tcp.analysis.retransmission","COUNT(tcp.analysis.duplicate_ack)tcp.analysis.duplicate_ack","COUNT(tcp.analysis.lost_segment) tcp.analysis.lost_segment","COUNT(tcp.analysis.fast_retransmission) tcp.analysis.fast_retransmission" | tail -2| head -1 > c.txt

a=`cat c.txt |cut -d "|" -f5`   # tcp retransmission
b=`cat c.txt |cut -d "|" -f6`	# number of duplicate acks
c=`cat c.txt |cut -d "|" -f7`   # number of lost segments 
d=`cat c.txt |cut -d "|" -f8`   # number of fast retransmission
e=`expr $a + $b+ $c+ $d`
#echo $a $b $c $d $e


# cnt varible stores total number of packets
cnt=`cat c.txt |cut -d "|" -f3`


# following script calculate MOS score, it takes two inputs :  total number of lost packets and total packets
python calculate-moss.py $e $cnt

