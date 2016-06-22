#This the main script which creates HTB queues and also calls the python scripts which classifies the flows

sudo bash create-htb-queues-laptop-AP.sh			
echo "htb created...."
sudo killall -9 tcpdump
sudo tcpdump -pni eth0 -s 100 -C 5 -w capture	&	
echo "tcpdump running..."
sudo python decision-tree-classification-laptop-AP.py

