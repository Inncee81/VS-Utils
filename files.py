import os, fnmatch, subprocess, errno, stat, glob
from subprocess import Popen, PIPE
from shutil import copy

## Add modules from the submodule (VS-Utils)
from prints import errmsg, debugmsg, infomsg

def files_find_ext(path, ext):
    ''' Find all files in a given path matching one or more extensions. '''

    exts = ext if isinstance(ext, str) else tuple(ext)

    ## if the passed path is a single file
    if os.path.isfile(path) and path.endswith(exts):
        if ("sample" not in os.path.basename(path)):
            return [path]

    ## If the passed path is a directory then search all files recursively
    ext_files = []
    for filename in glob.iglob(os.path.join(path, '') + '**/*', recursive=True):
        if os.path.isfile(filename) and filename.endswith(exts):
            if ("sample" not in filename):
                ext_files.append(filename)
    return sorted(ext_files)

def files_find_basename(path, basename):
    ''' Find all files in the given path with the extension. '''

    ext_files = []
    for root, _, filenames in os.walk(path):
        for filename in fnmatch.filter(filenames, "%s.*" % basename):
            if ("sample" not in filename):
                ext_files.append(os.path.join(root, filename))
    return ext_files

def file_copy(src, dst, args):
    ''' Copy file to directory and change owner and permissions. '''

    ## Without renaming the file
    file_name = os.path.basename(src)
    new_file_path = os.path.join(dst, file_name)
    copy(src, dst)
    os.chown(new_file_path, args.userid, args.groupid)
    mode = stat.S_IRWXU | stat.S_IROTH | stat.S_IRGRP
    os.chmod(new_file_path, mode)
    return new_file_path

def file_copy_args(dst, args):
    ''' Copy file to directory and change owner. '''

    ## Copy the video file to the specified destination
    new_file = file_copy(args.directory, dst, args)
    if not new_file:
        print("Error: Could not copy file (%s) to destination (%s)" % (args.directory, dst))
        return 0

    return new_file

def directory_create_owner(args):
    ''' Create a directory by the file name and change owner. '''

    dir_name = ".".join(args.name.split(".")[:-1])
    new_dir_path = os.path.join(args.directory, dir_name)
    if not os.path.exists(new_dir_path):
        os.mkdir(new_dir_path)
        os.chown(new_dir_path, args.userid, args.groupid)
    return new_dir_path

def create_path_directories(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def files_fix_single(args):
    """ If a single video file was downloaded create a directory and copy the file """

    abs_path = os.path.join(args.directory, args.name)
    if os.path.isfile(abs_path):
        new_dir = directory_create_owner(args)
        abs_path = file_copy(abs_path, new_dir, args)
        debugmsg("Fixed single video file into directory", "Postprocessing", (new_dir,))
    return abs_path

def files_unrar(abs_path, ext=None):
    """ Unzip rar files

    Arguments:
        abs_path {string} -- Path to the directory containg rar files
    """

    stderr = ""
    exts = ext if isinstance(ext, str) else tuple(ext)
    for rar_file in files_find_ext(abs_path, "rar"):
        files = []
        if (exts):
            process = Popen(["unrar", "lb", rar_file], stdout=PIPE, stderr=PIPE)
            stdout, stderr = process.communicate()
            if len(stderr) > 1: break
            files = stdout.decode("UTF-8").split("\n")
            files = [f for f in files if f.endswith(exts)]
        if (files or exts == None):
            infomsg("Found RAR archive in source directory, extract it", "Postprocessing", (rar_file,))
            process = Popen(["unrar", "x", "-o+", rar_file, abs_path], stdout=PIPE, stderr=PIPE)
            stderr = process.communicate()[1]
            if len(stderr) > 1: break

    if len(stderr) > 1:
        errmsg("Unrar archive failed with the following error message")
        print(stderr); exit()
