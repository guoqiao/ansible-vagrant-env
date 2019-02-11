#!/usr/bin/env python3
import sys
import json
import subprocess
import click


def run(cmd):
    """
    Run cmd in shell mode and get output, do not check return code.
    """
    return subprocess.run(cmd, check=False, shell=True, stdout=subprocess.PIPE).stdout.decode('utf-8')


def pretty_json(obj):
    return json.dumps(obj, indent=4, ensure_ascii=False)


def running_machines():
    cmd = 'vagrant status --machine-readable | grep state-human-short | grep running'
    # when grep get no result, it exit with 1
    output = run(cmd)
    hosts = []
    for line in output.splitlines():
        line = line.strip()
        if line:
            _, host, _, _ = line.split(',')
            hosts.append(host)
    return hosts


def ssh_config(host):
    cmd = 'vagrant ssh-config {}'.format(host)
    output = run(cmd)
    config = {}
    for line in output.splitlines():
        line = line.strip()
        if line:
            key, val = line.split(' ', 1)
            config[key] = val
    return config


def ansible_vars(ssh_config):
    return {
        'ansible_host': ssh_config['HostName'],  # 127.0.0.1
        'ansible_port': ssh_config['Port'],  # 2222
        'ansible_user': ssh_config['User'],  # vagrant
        'ansible_connection': 'ssh',
        'ansible_ssh_private_key_file': ssh_config['IdentityFile'],
    }


@click.command()
@click.option('--list', 'list_', is_flag=True, help='list all hosts')
@click.option('--host', help='list this host')
def main(list_, host):
    hostvars = {}
    hosts = running_machines()
    for host in hosts:
        hostvars[host] = ansible_vars(ssh_config(host))

    obj = {
        '_meta': {
            'hostvars': hostvars
        },
        'vagrant': hosts,
    }
    return print(pretty_json(obj))


if __name__ == '__main__':
    main()
