#!/bin/bash
# This script is meant for shadowfax setup, needed to be executed on shadowfax machine.
# It is used to make a bridge between the two interfaces iof the machine. It forwards all the packets from eth0 to eth1 interface and vice-versa.
#
sudo echo 1 > /proc/sys/net/ipv4/ip_forward                # enable IP forwarding
sudo iptables -A FORWARD -i eth0 -o eth1 -j ACCEPT         # forward all the packets from eth0 to eth1
sudo iptables -A FORWARD -i eth1 -o eth0 -j ACCEPT		   # forward all the packets from eth1 to eth0
