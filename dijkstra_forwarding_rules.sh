#!/bin/bash

# Forwarding rules for path: ['h2', 's1', 's15', 's0', 'h1']
sh ovs-ofctl add-flow s1 "dl_type=0x0806,action=flood"
sh ovs-ofctl add-flow s15 "dl_type=0x0806,action=flood"
sh ovs-ofctl add-flow s0 "dl_type=0x0806,action=flood"
