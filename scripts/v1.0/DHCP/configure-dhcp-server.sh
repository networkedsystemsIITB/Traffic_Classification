# This script make the system work as DHCP server.
# the server gets static IP as 172.16.1.70
# And client machines get IP range 172.16.1.10  to 172.16.1.50;
# gateway 172.16.1.60
# these things have been specified in dhcp.conf file


# simply run this sript as $ bash setup.sh

# it first copies these files at appropriate locations
sudo cp dhcpd.conf /etc/dhcp/          #added on 9 june
sudo cp interfaces /etc/network        #added on 9 june


#and then restarts the server

sudo ifconfig eth0 172.16.1.70
sudo service isc-dhcp-server stop
sudo service isc-dhcp-server start
sudo service isc-dhcp-server status
sudo /etc/init.d/networking restart
