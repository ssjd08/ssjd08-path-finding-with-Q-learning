#!/bin/bash

# Forwarding rules for path: ['h2', 's1', 's2', 'h5']
sh ovs-ofctl add-flow s1 "in_port=4,dl_type=0x0800,nw_dst=10.0.0.6,action=output:2"
sh ovs-ofctl add-flow s1 "in_port=2,dl_type=0x0800,nw_dst=10.0.0.3,action=output:4"
sh ovs-ofctl add-flow s2 "in_port=2,dl_type=0x0800,nw_dst=10.0.0.6,action=output:5"
sh ovs-ofctl add-flow s2 "in_port=5,dl_type=0x0800,nw_dst=10.0.0.3,action=output:2"
sh ovs-ofctl add-flow s1 "dl_type=0x0806,action=flood"
sh ovs-ofctl add-flow s2 "dl_type=0x0806,action=flood"
