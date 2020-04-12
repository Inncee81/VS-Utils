import os, re
from collections import namedtuple
from configparser import ConfigParser
from prints import errmsg

def enum(enum):
    return enum.replace(" ", "").split(",")

def parse_port(port):
    ''' Parse a port number '''

    try:
        if 1 <= int(port) <= 65535: return int(port)
        else: errmsg("Invalid port"); exit()
    except ValueError:
        errmsg("Invalid port"); exit()

def parse_docker_mappings():
    ''' Get all mounts of a docker container '''
    ## Get all mounts of the docker container
    import subprocess
    ps = subprocess.Popen(('mount'), stdout=subprocess.PIPE)
    output = subprocess.check_output(('grep', '^/dev/'), stdin=ps.stdout)
    ps.wait()

    ## Parse the output of the mount command
    mounts = [l for l in output.decode().split("\n") if len(l) > 0]
    mounts = [m for m in mounts if "/etc/" not in m.split(" ")[2] and m.split(" ")[2] != "/"]
    mounts = [m for m in mounts if "@docker" not in m]
    mounts = [(m.split()[2], m.split(",")[-1][:-1]) for m in mounts]
    mounts = [(m[0], m[1].split("=")[-1]) for m in mounts]
    mounts = [(m[0], m[1].replace("@syno", "volume1")) for m in mounts]
    return mounts

def parse_cfg_transmission(config, sections, fields, scope):

    ## Parse the config in case the script is running within a docker container
    if (scope == "docker"):
        mapping = parse_docker_mappings()
        handbrake = [m[0] for m in mapping if "handbrake" in m[0]]
        if (len(handbrake) > 0):
            handbrake = handbrake[0]
        else:
            errmsg("Define the handbrake mount in the container settings"); exit()

    ## Parse the config in case the script is running in host system
    else:
        mapping = None
        handbrake = enum(config.get(sections[2], fields[4]))
        if not os.path.isdir(handbrake):
            errmsg("Handbrake directory does not exist"); exit()
        watch_dirs = enum(config.get(sections[2], fields[6]))
        watch_dirs = [w.strip(os.sep) for w in watch_dirs.split(",") if os.path.isdir(w)]
        if not watch_dirs:
            errmsg("None of the watch directories exist"); exit()

    codecs = enum(config.get(sections[0], fields[1]))
    exts = enum(config.get(sections[0], fields[2]))
    server_port = parse_port(enum(config.get(sections[1], fields[3])))
    exclude = enum(config.get(sections[2], fields[5]))
    return (mapping, codecs, exts, exclude, server_port, handbrake, watch_dirs)

def parse_cfg_handbrake(config, sections, fields, scope):

    ## Get the different episode and movie paths
    handbrake_movies = enum(config.get(sections[0], fields[0]))
    handbrake_series = enum(config.get(sections[0], fields[1]))
    server_port = enum(config.get(sections[1], fields[2]))
    return (handbrake_movies, handbrake_series, server_port)

def parse_cfg(config_file, config_type, scope):
    ''' Parse all configuration options of the config file. '''

    ## Read the config file
    config = ConfigParser()
    config.read(config_file)

    ## VS-Handbrake
    if (config_type == "vs-handbrake"):
        sections = ["Handbrake", "SynoIndex"]
        fields = ["handbrake_movies", "handbrake_series", "synoindex_port"]

    ## VS-Transmission
    elif (config_type == "vs-transmission"):
        sections = ["Transmission", "SynoIndex", "Hostsystem"]
        fields = ["mapping", "codecs", "handbrake_exclude", "exclude",
                  "synoindex_port", "handbrake", "watch_directories"]
    else:
        errmsg("Config type not supported"); exit()

    ## Check whether all sections are present and initialize config Namespace
    _ = [exit('Error: Section (%s) missing' % s) for s in sections if not config.has_section(s)]
    cfg = namedtuple('cfg', " ".join(fields))
    cfg.__new__.__defaults__ = (None,) * len(cfg._fields)

    ## VS-Handbrake
    if (config_type == "vs-handbrake"):
        (movies, series, port) = parse_cfg_handbrake(config, sections, fields, scope)
        parsed_cfg = cfg(movies, series, port)

    ## VS-Transmission
    elif (config_type == "vs-transmission"):
        (mpg, cds, exts, excs, port, hb, dirs) = parse_cfg_transmission(config, sections, fields, scope)
        parsed_cfg = cfg(mpg, cds, exts, excs, port, hb, dirs)

    return parsed_cfg