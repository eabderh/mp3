#!/usr/bin/python


import subprocess
from subprocess import Popen
from subprocess import call
import re

import xml.etree.ElementTree as ET

def ssh_test_connection(targets):
    for target in targets:
        command = "ssh -o \"StrictHostKeyChecking=no\" {} exit".format(target)
        print command
        call(command, shell=True)
def exec_ssh_commands(targets, ssh_commands):
    for target in targets:
        for ssh_command in ssh_commands:
            command = "ssh {} \"{}\"".format(target, ssh_command)
            print command
            call(command, shell=True)
def exec_ssh_command_parallel(targets, ssh_command):
    processes = []
    for target in targets:
        command = "ssh {} \"{}\"".format(target, ssh_command)
        print command
        p = Popen(command, shell=True)
        processes.append(p)
    for p in processes: p.wait()
def exec_command(targets, command):
    for target in targets:
        formatted_command = command.format(target=target)
        print formatted_command
        call(formatted_command, shell=True)
def exec_remote_script(targets, script):
    for target in targets:
        command = "scp {} {}:.".format(script, target)
        print command
        call(command, shell=True)
    ssh_commands = ["sudo chmod +x " + script, "./" + script]
    exec_ssh_commands(targets, ssh_commands)
def scp_file(targets, source, filename, dest):
    for target in targets:
        s = source.format(hostname=target,filename=filename)
        d = dest.format(hostname=target,filename=filename)
        command = "scp {} {}".format(s,d)
        print command
        call(command, shell=True)
def parse_xmlfile(manifest_file):
    tree = ET.parse(manifest_file)
    root = tree.getroot()
    return root
def parse_xmltree_ssh(root):
    namespace = root.tag.split("}")[0] + "}"
    sshinfo = []
    node_sshinfo_t = dict.fromkeys(['host','user','hostname','port','identityfile'])
    node_sshinfo_t['identityfile'] = "~/.ssh/ssh_keys/geni/id_rsa"
    for node in root.findall(namespace + "node"):
        login = node.findall(".//" + namespace + "login")[-1]
        node_sshinfo = node_sshinfo_t.copy()
        node_sshinfo['host'] =       node.get("client_id")
        node_sshinfo['user'] =       login.get("username")
        node_sshinfo['hostname'] =   login.get("hostname")
        node_sshinfo['port'] =       login.get("port")
        sshinfo.append(node_sshinfo)
    sshinfo = sorted(sshinfo, key=lambda k: k['host'])
    return sshinfo
def sshinfo_allhosts(sshinfo):
    return [d['host'] for d in sshinfo]
def sshconfig_sprint(sshinfo):
    sshinfo = sorted(sshinfo, key=lambda k: k['host'])
    string = ""
    for node_sshinfo in sshinfo:
        string += host_entry_string(node_sshinfo)
    return string
def sshconfig_fprint(sshinfo, config_file):
    fout = open(config_file, 'w')
    for node_sshinfo in sshinfo:
        fout.write(host_entry_string(node_sshinfo))
    fout.close()
def host_entry_string(node_sshinfo):
    host_string =  "\nHost "            + node_sshinfo['host']
    host_string += "\n\tUser "          + node_sshinfo['user']
    host_string += "\n\tHostname "      + node_sshinfo['hostname']
    host_string += "\n\tPort "          + node_sshinfo['port']
    host_string += "\n\tIdentityFile "  + node_sshinfo['identityfile']
    return host_string



def parse_log(targets, log_formatname):
    l = dict()
    for target in targets:
        ifconfig_logname = log_formatname.format(target=target,logfile="ifconfig-log.txt")
        route_logname = log_formatname.format(target=target,logfile="route-log.txt")
        ifconfig = dict(parse_ifconfig(ifconfig_logname))
        route = dict(parse_route(targets, route_logname))
        listoftuples = [(route[id],ifconfig[id]) for id in set(route) & set(ifconfig)]
        l[target] = dict(listoftuples)
    return l
def parse_route(targets, route_logfile):
    l = []
    with open(route_logfile, 'r') as f:
        string = f.read()
    for target in targets:
        for line in string.split("\n"):
            if target in line:
                eth = line[-4:len(line)]
                l.append((eth, target))
                break
    return l
def parse_ifconfig(logfile):
    with open(logfile, 'r') as f:
        string = f.read()
    return re.findall(r'^(\S+).*?inet addr:(\S+)', string, re.S | re.M)
def buildcfg(targets, routeinfo):
    conntemplate1 = "add listener udp udp{int} {localip} 9695\n"
    conntemplate2 = "add connection udp conn{remotehost} {remoteip} 9695 {localip} 9695\n"
    routetemplate = "add route conn{remotehost} lci:/ 1\n"
    print routeinfo
    for target in targets:
        f = open("metis.cfg", 'w')
        f.write( "add listener tcp local0 127.0.0.1 9695\n")
        for n, connection in enumerate(routeinfo[target]):
            type(connection)
            print connection
            print target
            localip = routeinfo[target][connection]
            remoteip = routeinfo[connection][target]
            print localip
            f.write( conntemplate1.format(int=n, \
                    localip=localip))
            f.write( conntemplate2.format( \
                    localip=localip, \
                    remoteip=remoteip, \
                    remotehost=connection))
        for connection, n in enumerate(routeinfo[target]):
            f.write( routetemplate.format(remotehost=connection))
        f.write("list connections\nlist routes\n")
        command = "scp metis.cfg " + target + ":/CCNx_Distillery/usr/bin"
        call(command, shell=True)
    f.close()


def make_sshconfig(manifest_file):
    root = parse_xmlfile(manifest_file)
    sshinfo = parse_xmltree_ssh(root)
    print sshconfig_sprint(sshinfo)
def make_sshconfigfile(manifest_file, sshconfig_file):
    root = parse_xmlfile(manifest_file)
    sshinfo = parse_xmltree_ssh(root)
    sshconfig_fprint(sshinfo, sshconfig_file)





