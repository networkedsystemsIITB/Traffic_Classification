#!/bin/bash

# This script is executed on shadowfax machine.
#It is used for natting. It translates private ip to public ip for all the packets going outside of the private network, i.e. packets going to the Internet. Similarly, it translates public ip to private ip for all the packets coming from Internet. It changes the source IP of the packets going to the Internet, to its own IP address (masquerade), i.e. desktop’s eth0 IP address


sudo ifconfig eth1 172.16.1.60    										# assign static IP for gateway
sudo iptables -P FORWARD ACCEPT   										# disabling the firewall
sudo iptables --table nat -A POSTROUTING -o eth0 -j MASQUERADE			# iptables rules for natting
