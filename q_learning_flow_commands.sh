#!/bin/bash

# Forwarding rules for path: ['h1', 's0', 's3', 's4', 's1', 'h2']
/usr/bin/ovs-ofctl add-flow s0 "in_port=2,dl_type=0x0800,nw_dst=10.0.1.1,action=output:3"
/usr/bin/ovs-ofctl add-flow s0 "in_port=3,dl_type=0x0800,nw_dst=10.0.0.2,action=output:2"
/usr/bin/ovs-ofctl add-flow s3 "in_port=3,dl_type=0x0800,nw_dst=10.0.1.1,action=output:4"
/usr/bin/ovs-ofctl add-flow s3 "in_port=4,dl_type=0x0800,nw_dst=10.0.0.2,action=output:3"
/usr/bin/ovs-ofctl add-flow s4 "in_port=3,dl_type=0x0800,nw_dst=10.0.1.1,action=output:4"
/usr/bin/ovs-ofctl add-flow s4 "in_port=4,dl_type=0x0800,nw_dst=10.0.0.2,action=output:3"
/usr/bin/ovs-ofctl add-flow s1 "in_port=3,dl_type=0x0800,nw_dst=10.0.1.1,action=output:1"
/usr/bin/ovs-ofctl add-flow s1 "in_port=1,dl_type=0x0800,nw_dst=10.0.0.2,action=output:3"
/usr/bin/ovs-ofctl add-flow s0 "dl_type=0x0806,action=flood"
/usr/bin/ovs-ofctl add-flow s3 "dl_type=0x0806,action=flood"
/usr/bin/ovs-ofctl add-flow s4 "dl_type=0x0806,action=flood"
/usr/bin/ovs-ofctl add-flow s1 "dl_type=0x0806,action=flood"
