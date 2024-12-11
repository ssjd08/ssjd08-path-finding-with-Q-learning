#!/bin/bash

# Forwarding rules for path: ['h2', 's2', 's3', 's9', 's1', 'h1']
sh ovs-ofctl add-flow s2 "dl_type=0x0806,action=flood"
sh ovs-ofctl add-flow s3 "dl_type=0x0806,action=flood"
sh ovs-ofctl add-flow s9 "dl_type=0x0806,action=flood"
sh ovs-ofctl add-flow s1 "dl_type=0x0806,action=flood"
