import os, re
from collections import namedtuple
from configparser import ConfigParser
from prints import errmsg, debugmsg

def enum(enum):
    return enum.replace(" ", "").split(",")

def parse_dig(dig, imin, imax):
    ''' Parse a digit '''

    dig = enum(dig)[0]
    try:
        if imin <= int(dig) <= imax: return int(dig)
        else: errmsg("Invalid digit in config"); exit()
    except ValueError:
        errmsg("Invalid digit in config"); exit()

def parse_strlist(strlist, paths=False):
    try:
        strlist = list(filter(None, strlist.split(',')))
    except ValueError:
        errmsg("Invalid string list in config"); exit()
    if not strlist:
        errmsg("Invalid string list in config"); exit()
    if paths:
        paths = [p.strip(os.sep) for p in strlist if os.path.isdir(p)]
        if not paths:
            errmsg("Config contains list of non-existent file paths")
        if set(paths) != set(strlist):
            debugmsg("Config contains path which does not exist")
        return paths
    return strlist

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

def parse_cfg_transmission(cfg, scope):

    mapping, host_watch_dir = (None for _ in range(2))

    ## Parse the config in case the script is running within a docker container
    if (scope == "docker"):
        mapping = parse_docker_mappings()
        handbrake = [m[0] for m in mapping if "handbrake" in m[0]]
        if (len(handbrake) > 0):
            handbrake = handbrake[0]
        else:
            errmsg("Define the handbrake mount in the container settings"); exit()

    ## [Hostsystem] Parse the config in case the script is running in host system
    else:
        handbrake = parse_strlist(cfg.get("Host", "host_handbrake"), True)[0]
        host_watch_dir = parse_strlist(cfg.get("Host", "host_watch_dir"), True)

    codecs = enum(cfg.get("Transmission", "codecs"))
    extensions = enum(cfg.get("Transmission", "extensions"))
    port = parse_dig(cfg.get("SynoIndex", "synoindex_port"), 1, 65535)
    handbrake_exclude = parse_strlist(cfg.get("Handbrake", "handbrake_exclude"))

    return (mapping, codecs, extensions, port, handbrake_exclude,
            handbrake, host_watch_dir)

def parse_cfg_handbrake(cfg, scope):

    ## Get the different episode and movie paths
    handbrake_movies = enum(cfg.get("Handbrake", "handbrake_movies"))
    handbrake_series = enum(cfg.get("Handbrake", "handbrake_series"))
    handbrake_original = parse_dig(cfg.get("Handbrake", "handbrake_original"), 0, 3)
    port = parse_dig(cfg.get("SynoIndex", "synoindex_port"), 1, 65535)
    return (handbrake_movies, handbrake_series, handbrake_original, port)

def parse_cfg(config_file, config_type, scope):
    ''' Parse all configuration options of the config file. '''

    ## Read the config file
    config = ConfigParser()
    config.read(config_file)

    ## VS-Handbrake
    if (config_type == "vs-handbrake"):
        sections = ["Handbrake", "SynoIndex"]
        fields = ["movies", "series", "original", "port"]

    ## VS-Transmission
    elif (config_type == "vs-transmission"):
        sections = ["Transmission", "SynoIndex", "Handbrake", "Host"]
        fields =   ["mapping", "codecs", "extensions", "port", "exclude",
                    "handbrake", "watch_dir"]
    else:
        errmsg("Config type not supported"); exit()

    ## Check whether all sections are present and initialize config Namespace
    _ = [exit('Error: Section (%s) missing' % s) for s in sections if not config.has_section(s)]
    cfg = namedtuple('cfg', " ".join(fields))
    cfg.__new__.__defaults__ = (None,) * len(cfg._fields)

    ## VS-Handbrake
    if (config_type == "vs-handbrake"):
        (movies, series, original, port) = parse_cfg_handbrake(config, scope)
        parsed_cfg = cfg(movies, series, original, port)

    ## VS-Transmission
    elif (config_type == "vs-transmission"):
        (mpg, cds, exts, port, excls, hb, dirs) = parse_cfg_transmission(config, scope)
        parsed_cfg = cfg(mpg, cds, exts, port, excls, hb, dirs)

    return parsed_cfg