#!/usr/bin/python

import geni_lib as gl
from geni_lib import *
import subprocess
from subprocess import call

class geni:
    def init(self):
        self.root = gl.parse_xmlfile(self.manifest_file)
        self.sshinfo = gl.parse_xmltree_ssh(self.root)
        self.targets = gl.sshinfo_allhosts(self.sshinfo)
    def makesshconfig(self):
        self.sshconfig_string = gl.sshconfig_sprint(self.sshinfo)
        gl.sshconfig_fprint(self.sshinfo, self.sshconfig_file)
    def testssh(self):
        gl.ssh_test_connection(self.targets)
    def getinfo(self):
        gl.exec_ssh_commands(self.targets,
            ["route > route-log",
            "ifconfig > ifconfig-log"])
        log_filename = self.log_formatname.format(target="{target}",logfile="route-log")
        command = "scp {target}:route-log " + log_filename
        gl.exec_command(self.targets, command)
        log_filename = self.log_formatname.format(target="{target}",logfile="ifconfig-log")
        command = "scp {target}:ifconfig-log " + log_filename
        gl.exec_command(self.targets, command)
    def configure(self):
        command = "scp routeconfig.sh {target}:."
        gl.exec_command(self.targets, command)
        commands = ["sudo chmod +x routeconfig.sh"]
        gl.exec_ssh_commands(self.targets, commands)
    def test(self):
        commands = ["sudo ifconfig eth1 netmask 255.255.0.0", \
            "sudo ifconfig eth2 netmask 255.255.0.0", \
            "sudo ifconfig eth3 netmask 255.255.0.0", \
            "sudo ifconfig eth4 netmask 255.255.0.0", \
            "sudo ifconfig eth5 netmask 255.255.0.0"]
        gl.exec_ssh_commands(self.targets, commands)
    def restart(self):
        commands = ["sudo /etc/init.d/quagga restart"]
        gl.exec_ssh_commands(self.targets, commands)
    def stop(self):
        commands = ["sudo /etc/init.d/quagga stop"]
        gl.exec_ssh_commands(self.targets, commands)
    def buildconfig(self):
        self.routeinfo = gl.parse_log(self.targets, self.log_formatname)
        gl.buildcfg(self.targets, self.routeinfo)




