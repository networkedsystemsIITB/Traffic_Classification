#This the main script which creates HTB queues and also calls the python scripts which classifies the flows

sudo bash create-htb-queues.sh			
echo "htb created...."
sudo killall -9 tcpdump
sudo tcpdump -pni eth1 -s 100 -C 10 -w capture	&	
echo "tcpdump running..."
sudo python knn-classification-script.py

