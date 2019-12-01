import os, re
from ConfigParser import ConfigParser
from collections import namedtuple

config_types = ["vs-transmission", "vs-handbrake", "vs-synoindex"]

def enum(enum):
    return enum.replace(" ", "").split(",")

def get_docker_ip(scope):
    ''' Get the docker0 IP address with or without external packages. '''

    if scope == "host":
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

def parse_cfg_transmission(config, sections, fields, scope):

    ## Get all mappings from the config and check whether they exist
    mapping = config._sections['Mapping']
    mapping = [m for m in list(mapping.items()) if m[0] != "__name__"]
    for m in mapping:
        check_path = m[1] if scope == "host" else m[0]
        if not os.path.exists(check_path):
            exit("Error: Mapping path doesnt exist: (%s)" % check_path)

    ## Get all handbrake related configs
    handbrake = config.get(sections[1], fields[1])
    codecs = enum(config.get(sections[1], fields[2]))

    return (mapping, handbrake, codecs)

def parse_cfg_handbrake(config, sections, fields, scope):

    ## Get the different episode and movie paths
    handbrake_movies = enum(config.get(sections[0], fields[0]))
    handbrake_series = enum(config.get(sections[0], fields[1]))

    return (handbrake_movies, handbrake_series)

def parse_cfg_synoindex(config, sections, fields, scope):

    ## Get all server configurations from config file
    ip = get_docker_ip(scope)
    port = int(config.get(sections[0], 'server_port'))
    url = "http://%s:%s" % (ip, port)

    ## Get the debug files
    server_logs = config.get(sections[0], fields[3])
    client_logs = config.get(sections[1], fields[4])

    return (ip, port, url, server_logs, client_logs)

def parse_cfg(config_file, config_type, scope):
    ''' Parse all configuration options of the config file. '''

    ## Check whether the config type is supported
    if config_type not in config_types:
        exit("Error: Config type is not supported: %s" % (config_type))

    ## Read the config file
    config = ConfigParser()
    config.read(config_file)

    ## VS-Transmission
    if (config_type == "vs-transmission"):
        sections = ['Mapping', 'Handbrake']
        fields = ["mapping", "handbrake", "codecs"]

    ## VS-Handbrake
    elif (config_type == "vs-handbrake"):
        sections = ['Handbrake']
        fields = ["handbrake_movies", "handbrake_series"]

    ## VS-SynoIndex
    elif (config_type == "vs-synoindex"):
        sections = ["Server", "Client"]
        fields = ["port", "ip", "url", "server_logs", "client_logs"]

    ## Check whether all sections are present and initialize config Namespace
    _ = [exit('Error: Section (%s) missing' % s) for s in sections if not config.has_section(s)]
    cfg = namedtuple('cfg', " ".join(fields))
    cfg.__new__.__defaults__ = (None,) * len(cfg._fields)

    if (config_type == "vs-transmission"):
        (mapping, handbrake, codecs) = parse_cfg_transmission(config, sections, fields, scope)
        parsed_cfg = cfg(mapping, handbrake, codecs)

    if (config_type == "vs-handbrake"):
        (handbrake_movies, handbrake_series) = parse_cfg_handbrake(config, sections, fields, scope)
        parsed_cfg = cfg(handbrake_movies, handbrake_series)

    if (config_type == "vs-synoindex"):
        (ip, port, url, server_logs, client_logs) = parse_cfg_synoindex(config, sections, fields, scope)
        parsed_cfg = cfg(port, ip, url, server_logs, client_logs)

    return parsed_cfg

def parse_dockerpath(mapping, filepath):
    """ Convert a path within docker container to hostsystem path. """

    ## General validation
    if not any(m[0] in filepath for m in mapping):
        return -1

    ## Replace the docker path to the host path
    for m in mapping:
            file_tmp = filepath.replace(m[0], m[1])
            if file_tmp != filepath:
                (source_host, root_host) = (file_tmp, m[1])
    return (source_host, root_host)