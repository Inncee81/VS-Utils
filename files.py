import os, sys, fnmatch, subprocess, errno
from subprocess import Popen, PIPE, STDOUT, call
from shutil import copy, copyfile

def files_find_ext(path, ext):
	''' Find all files in the given path with the extension. '''

	ext_files = []
	for root, _, filenames in os.walk(path):
		for filename in fnmatch.filter(filenames, "*.%s" % ext):
			if ("sample" not in filename):
				ext_files.append(os.path.join(root, filename))
	return ext_files

def file_copy(src, dst, args):
	''' Copy file to directory and change owner. '''

	## Without renaming the file
	file_name = os.path.basename(src)
	new_file_path = os.path.join(dst, file_name)
	if not os.path.exists(new_file_path):
		copy(src, dst)
		os.chown(new_file_path, args.userid, args.groupid)
		return dst

	return 0

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

def crate_path_directories(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def unrar_files(abs_path):
	""" Unzip rar files (synochronous)

	Arguments:
		abs_path {string} -- Path to the directory containg rar files
	"""

	rar_files = files_find_ext(abs_path, "rar")
	if rar_files:
		print("Found some rar files: " + ", ".join(rar_files))
		for rar_file in rar_files:
			print("rar file \"%s\", try to unrar it" % (rar_file))
			process = Popen(["unrar", "x", "-o+", rar_file, abs_path], stdout=PIPE, stderr=PIPE)
			stderr = process.communicate()[1]
			print(stderr)