#!/bin/bash

br_name="br1"
br_fail_mode="secure"
br_datapath_id="3333333333abcdef"

p_no_wan="50"
p_type_wan="te"
p_tag_wan="1"
p_trunks_wan="1002"

p_no_mgmt="48"
p_type_mgmt="ge"
p_tag_mgmt="1002"

p_no_srv="4"
p_type_srv="ge"
p_tag_srv="1002"

ctrlr_ip="150.225.14.200"
ctrlr_ip_bk="10.10.30.1"
mgmt_ip="150.225.14.209"
mgmt_mask="24"
mgmt_iface="eth0"
br_ip="10.10.30.209"
br_mask="24"
gateway_ip="150.225.14.22"
gateway_iface="${mgmt_iface}"

# Remove all bridges
echo -e "\n* Remove all bridges in the switch."
br_all=$(ovs-vsctl --no-heading --columns=name -d bare list bridge)
if [ -n ${br_all} ]; then
    for br in ${br_all}
    do 
        echo -e "  - Removing ${br} ...\n"
        ovs-vsctl del-br ${br}
    done
fi

# Add bridge
echo -e "\n* Add bridge ${br_name}."
ovs-vsctl add-br ${br_name} \
    -- set Bridge ${br_name} \
    datapath_type=pica8 \
    fail_mode=${br_fail_mode} \
    other-config=datapath-id=${br_datapath_id}

# Add ports
echo -e "\n* Add ports to ${br_name}."

echo -e "  - Adding port to WAN ...\n"
ovs-vsctl add-port ${br_name} \
    ${p_type_wan}-1/1/${p_no_wan} \
    vlan_mode=trunk \
    tag=${p_tag_wan} \
    trunks=${p_trunks_wan} \
    -- set Interface ${p_type_wan}-1/1/${p_no_wan} \
    type=pica8 \
    options:link_speed=1G

echo -e "  - Adding port to MGMT network ...\n"
ovs-vsctl add-port ${br_name} \
    ${p_type_mgmt}-1/1/${p_no_mgmt} \
    vlan_mode=access \
    tag=${p_tag_mgmt} \
    -- set Interface ${p_type_mgmt}-1/1/${p_no_mgmt} \
    type=pica8

echo -e "  - Adding port to server ...\n"
ovs-vsctl add-port ${br_name} \
    ${p_type_srv}-1/1/${p_no_srv} \
    vlan_mode=access \
    tag=${p_tag_srv} \
    -- set Interface ${p_type_srv}-1/1/${p_no_srv} \
    type=pica8

# Add flows
echo -e "\n* Add flows to ${br_name}."

ovs-ofctl add-flow ${br_name} \
table=0,cookie=0x11,priority=2000,idle_timeout=0,hard_timeout=0,\
in_port=${p_no_wan},dl_type=0x0800,nw_dst=${mgmt_ip},\
actions=output:${p_no_mgmt}

ovs-ofctl add-flow ${br_name} \
table=0,cookie=0x12,priority=2000,idle_timeout=0,hard_timeout=0,\
in_port=${p_no_mgmt},dl_type=0x0800,nw_dst=${ctrlr_ip},\
actions=output:${p_no_wan}

# ovs-ofctl add-flow ${br_name} \
# table=0,cookie=0x13,priority=2000,idle_timeout=0,hard_timeout=0,\
# in_port=${p_no_wan},dl_type=0x0800,nw_dst=${br_ip},\
# actions=output:local

# ovs-ofctl add-flow ${br_name} \
# table=0,cookie=0x14,priority=2000,idle_timeout=0,hard_timeout=0,\
# in_port=local,dl_type=0x0800,nw_dst=${ctrlr_ip_bk},\
# actions=output:${p_no_wan}

ovs-ofctl add-flow ${br_name} \
table=0,cookie=0x21,priority=2000,idle_timeout=0,hard_timeout=0,\
in_port=${p_no_wan},dl_type=0x0806,nw_dst=${mgmt_ip},\
actions=output:${p_no_mgmt}

ovs-ofctl add-flow ${br_name} \
table=0,cookie=0x22,priority=2000,idle_timeout=0,hard_timeout=0,\
in_port=${p_no_mgmt},dl_type=0x0806,nw_dst=${ctrlr_ip},\
actions=output:${p_no_wan}

# ovs-ofctl add-flow ${br_name} \
# table=0,cookie=0x23,priority=2000,idle_timeout=0,hard_timeout=0,\
# in_port=${p_no_wan},dl_type=0x0806,nw_dst=${br_ip},\
# actions=output:local

# ovs-ofctl add-flow ${br_name} \
# table=0,cookie=0x24,priority=2000,idle_timeout=0,hard_timeout=0,\
# in_port=local,dl_type=0x0806,nw_dst=${ctrlr_ip_bk},\
# actions=output:${p_no_wan}

# Reset IP addresses
echo -e "\n* Reset IP settings."
sudo ip route flush scope link
sudo ip route del default
sudo ip addr flush scope global

# Set IP addresses
echo -e "\n* Set IP addresses."

echo -e "  - Adding bridge IP ...\n"
sudo ip addr add ${br_ip}/${br_mask} dev ${br_name}

echo -e "  - Adding management IP ...\n"
sudo ip addr add ${mgmt_ip}/${mgmt_mask} dev ${mgmt_iface}

echo -e "  - Adding default route ...\n"
sudo ip route add default via ${gateway_ip} dev ${gateway_iface}
