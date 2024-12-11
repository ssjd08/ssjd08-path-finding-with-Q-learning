#!/bin/bash

# Forwarding rules for path: ['h2', 's2', 'h3', 'h1']
sh ovs-ofctl add-flow s2 "dl_type=0x0806,action=flood"
