import os, re, urllib, socket, struct
from ConfigParser import ConfigParser
from collections import namedtuple

cfg = namedtuple('cfg', 'port ip url server_logs client_logs mapping handbrake')

cfg.__new__.__defaults__ = (None,) * len(cfg._fields)

synoindex_modes = ['a']

def get_docker_ip(mode):
	''' Get the docker0 IP address with or without external packages. '''

	if mode == "server":
		import netifaces as ni
		ni.ifaddresses('docker0')
		ip = ni.ifaddresses('docker0')[ni.AF_INET][0]['addr']
	else:
		import subprocess
		ps = subprocess.Popen(('ip', 'route', 'show'), stdout=subprocess.PIPE)
		output = subprocess.check_output(('grep', 'default'), stdin=ps.stdout)
		ps.wait()
		ip = re.search(r'([0-9]{1,3}[\.]){3}[0-9]{1,3}', output, flags=0).group()
	return ip

def parse_cfg(config_file, mode):
	''' Parse all configuration options of the config file. '''

	## Read the config file
	config = ConfigParser()
	config.read(config_file)
	secs = ['Server', 'Client', 'Mapping', 'Handbrake']
	_ = [exit('Error: Section missing') for s in secs if not config.has_section(s)]

	## Get all server configurations from config file
	ip = get_docker_ip(mode)
	port = int(config.get(secs[0], 'server_port'))
	url = "http://%s:%s" % (ip, port)

	## Get the debug files
	server_logs = config.get(secs[0], 'server_logs')
	client_logs = config.get(secs[1], 'client_logs')

	## Get all mappings from the config and check whether they exist
	mapping = config._sections['Mapping']
	mapping = [m for m in list(mapping.items()) if m[0] != "__name__"]
	for m in mapping:
		check_path = m[1] if mode == "server" else m[0]
		if not os.path.exists(check_path):
			exit("Error: Mapping path doesnt exist: \"" + check_path + "\"")

	## Get all handbrake related configs
	handbrake = config.get(secs[3], 'handbrake_output')

	return cfg(port, ip, url, server_logs, client_logs, mapping, handbrake)

def validate_input(mapping, option, filepath):
	""" Validate the query arguments. """

	## General validation
	if(option not in synoindex_modes): return -1
	if not any(m[0] in filepath for m in mapping): return -2

	## Replace the docker path to the host path
	for m in mapping: filepath = filepath.replace(m[0], m[1])
	return filepath