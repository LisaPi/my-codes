#! /usr/bin/env python

# import
import re
import os
import json

# Get all contents into subject
fobj = open('flow.txt')
subject = fobj.readlines()
fobj.close()

for line in subject:
    post_subject = {}

    post_subject.setdefault('dpid', 6790988926532229681L)
    for imatch in ['cookie', 'priority', 'idle_timeout', 'hard_timeout']:
        is_match = re.search("%s=([a-zA-Z0-9]+)" % imatch, line)
        if is_match:
            match_value = is_match.group(1)
            if re.search("0x", match_value):
                post_subject['%s' % imatch] = int(match_value, 16)
            else:
                post_subject['%s' % imatch] = match_value

    post_subject.setdefault('match', {})
    for imatch in ['in_port', 'dl_type', 'nw_proto', 'nw_dst', 'tp_dst', 'tp_src', 'dl_vlan', 'arp_op']:
        is_match = re.search("%s=([a-zA-Z0-9.]+)" % imatch, line)
        if is_match:
            match_value = is_match.group(1)
            if re.search("0x", match_value):
                post_subject['match']['%s' % imatch] = int(match_value, 16)
            else:
                post_subject['match']['%s' % imatch] = match_value

    post_subject.setdefault('actions', [])
    is_match = re.search("actions=output:([a-zA-Z0-9]+)", line)
    if is_match:
        match_value = is_match.group(1)
        post_subject['actions'] = [{"type":"OUTPUT", "port": match_value}]

    #print post_subject
    result = json.dumps(post_subject, indent=1)
    print result
    os.system("curl -X POST -d '%s' http://10.10.50.42:8080/stats/flowentry/add" % result)
