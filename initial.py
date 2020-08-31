#! /usr/bin/env python3.8

from fabric import Connection, env
import argparse
import getpass

parser = argparse.ArgumentParser(
    description='To verify the access to the server and fetching some details')
parser.add_argument(
    'serverlist', help='Text file containg server list')
parser.add_argument('username', help='Username for login')

args = parser.parse_args()
username = args.username.lower()
loginpass = getpass.getpass(prompt='Enter login Password: ')

env.disable_known_hosts = True

def read_server_list(inputlist):
    """This function returns the list of unique servers from input servers list"""
    hostlist = []
    with inputlist:
        servers = f.readlines()
        inputnodups = list(set(servers))
        for line in inputnodups:
            if not line.isspace():
                hostlist.append(line.strip())
    return hostlist
try:
    f = open(args.serverlist)
except Exception as error:
    print(error)
except FileNotFoundError as err:
    print(f"Exception : {err}")

else:
    c = Connection(host="13.235.76.163", port=22, user="cloud_user", connect_timeout='5',
                   connect_kwargs={'password': loginpass})
    hostname = c.run('hostname', warn=True, hide=True)
    hostlist = read_server_list(f)
    print(f"Server connected : {c.is_connected}")
    result = c.run("uname -z", warn=True, hide=True)
    print(f"this is result value: {result}")
    print(f"this is stdout : {result.stdout}")
    c.close()
    print(f"Server still connected?? {c.is_connected}")
