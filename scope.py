import os

def scope_map_docker_path(mapping, filepath):
    """ Convert a path within docker container to hostsystem path.

    Arguments:
        mapping {list}      -- List of tuple representing the docker container mounts.
        filepath {string}   -- File path which should be mapped.

    Returns:
        tuple  -- Tuple (source (host), root directory of source (host), root of source in container)
    """

    ## Sanity check
    if not any(m[0] in filepath for m in mapping):
        return -1

    ## Map the docker path to the host path
    for m in mapping:
            file_tmp = filepath.replace(m[0], m[1])
            if file_tmp != filepath:
                (source_host, root_host, root) = (file_tmp, m[1], m[0])
    return (source_host, root_host, root)

def scope_map_path(cfg, args, filepath):
    """ Map docker path to host system path if necessary. If the scope
        is the host system the original path remains unchanged. The root
        directory is selected using the watch directories.

    Arguments:
        cfg {Namespace}     -- Namespace containing all configurations
        args {Namespace}    -- Namespace containing all shell arguments
        filepath {string}   -- File path which should be mapped.

    Returns:
        tuple  -- Tuple (source (host), root directory of source (host), root of source (current scope))
    """

    ## Map docker path to host system path
    if (args.scope == "docker"):
        return scope_map_docker_path(cfg.mapping, filepath)

    ## If script runs under host system then use the watch directories
    else:
        watch_dirs = cfg.watch_directories + [cfg.handbrake]
        maps = [(filepath, d) for d in watch_dirs if d in filepath]
        if not maps: return -1
        (source_host, root_host) = maps[0]
        return (source_host, root_host, root_host)

def scope_reverse_map_path(cfg, args, filepath):
    """ Docker-scope: hostsystem path -> docker path
        Host-scope:   hostsystem path -> hostsystem path """

    ## Use original path if not docker scope
    if (args.scope != "docker"):
        return filepath

    ## Map host system path to docker path
    for m in cfg.mapping:
        file_tmp = filepath.replace(m[1], m[0])
        if file_tmp != filepath:
            return file_tmp

def scope_get():
    """ Get the scope of the script (within docker container or host system). """

    cgroup_path = os.path.join(os.sep, "proc", "1" , "cgroup")
    with open(cgroup_path, 'r') as f: groups = f.readlines()
    groups = list(set([g.replace("\n","").split(":")[-1] for g in groups]))
    if (len(groups) == 1 and groups[0] == os.sep):
        return "host"
    return "docker"