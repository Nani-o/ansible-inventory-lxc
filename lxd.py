#!/usr/bin/python
# -*- coding: utf-8 -*-

import optparse
import json
import subprocess
import sys
import os

def execute_command(command):
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result = proc.communicate()[0]
    return result

def get_inventory(show_meta_hostvars):
    group = "LXD_CONTAINERS"

    if show_meta_hostvars:
        host_list = {
            "_meta": {
                "hostvars": {}
            }
        }
    else:
        host_list = {}

    host_list[group] = {'hosts': []}

    containers_path = '/sys/fs/cgroup/devices/lxc.monitor'
    for container in [f for f in os.listdir(containers_path) if os.path.isdir(os.path.join(containers_path, f))]:
        host_list[group]['hosts'].append(container)
        if show_meta_hostvars:
            host_list['_meta']['hostvars'][container] = {
                "ansible_connection": "lxd"
            }

    return host_list

def get_host(host):
    inventory = get_inventory(True)
    hostvars = inventory['_meta']['hostvars']
    if host in hostvars.keys():
        vars = hostvars[host]
    else:
        vars = {}

    return vars

def main():
    parser = optparse.OptionParser()
    parser.add_option('--list', action='store_true', dest='list',
                      default=False, help='List lxd containers')
    parser.add_option('--host', dest='host', default=None, metavar='HOST',
                      help='List vars for an lxd container')
    parser.add_option('--pretty', action='store_true', dest='pretty',
                      default=False, help='Pretty print du JSON')
    parser.add_option('--no-meta-hostvars', action='store_false',
                      dest='meta_hostvars', default=True,
                      help='Remove meta hostvars')
    options, args = parser.parse_args()

    if options.host is not None:
        inventory = get_host(options.host)
    else:
        inventory = get_inventory(options.meta_hostvars)

    json_kwargs = {}
    if options.pretty:
        json_kwargs.update({'indent': 4, 'sort_keys': True})
    json.dump(inventory, sys.stdout, **json_kwargs)


if __name__ == '__main__':
    main()
