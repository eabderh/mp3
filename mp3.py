#!/usr/bin/python

import geni_interface as gi

mp = gi.geni()
mp.manifest_file = "manifest.xml"
mp.sshconfig_file = "mp3_sshconfig.txt"
mp.log_formatname = "log/{target}_{logfile}"
mp.init()

