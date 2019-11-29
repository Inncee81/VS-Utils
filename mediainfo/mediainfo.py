import subprocess, sys, os, collections, logging
from datetime import datetime

## Set the logger and its level
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def ffprobe_file(file_name):
	''' Execute the ffprobe command to get all media information. '''

	cmds = ['ffprobe', '-v', 'error', '-show_format', '-show_streams', file_name.encode('UTF-8')]
	logger.debug("ffprobe -v error -show_format -show_streams %s" % file_name.encode('UTF-8'))
	p = subprocess.Popen(cmds, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
	stderr=subprocess.PIPE)
	output, _ = p.communicate()
	if (output == None or output == ""):
		return None

	stream_dict = ffprobe_parse(output)
	return ffprobe_filter(stream_dict)

def ffprobe_parse(format_string):
	''' Parse the ffprobe output into a stream-based list of dictionaries. '''

	stream_list = []; format_info = {}
	for line in format_string.split('\n'):
		if "[/STREAM]" in line:
			stream_list.append(("Stream", format_info))
			format_info = {}
		elif "[/FORMAT]" in line:
			stream_list.append(("Format", format_info))
			format_info = {}
		elif '=' in line:
			k, v = line.split('=')
			k = k.strip()
			v = v.strip()
			format_info[k] = v
	stream_list = [("%s %s" % (s[0], s[1]['index']), s[1]) if s[0] == "Stream" else s for s in stream_list]
	return stream_list

def ffprobe_filter(stream_list):
	''' Transforms the ffprobe output to a ordered dict with
		all information needed by the SynoIndex. '''

	media_infos = collections.OrderedDict()

	## Get the stream and format dictionaries
	video_stream = [s for s in stream_list if s[0] != "Format" and s[1]['codec_type'] == 'video'][0][1]
	audio_stream = [s for s in stream_list if s[0] != "Format" and s[1]['codec_type'] == 'audio' and s[1]['TAG:language'] == "ger"][0][1]
	format_info = [s for s in stream_list if s[0] == "Format"][0][1]

	## General file information
	media_infos['path'] = format_info['filename']
	album, title = media_infos['path'].split('/')[-2:]
	media_infos['title'] = title
	media_infos['filesize'] = format_info['size']
	media_infos['album'] = album

	## Video
	media_infos['container_type'] = format_info['format_name']
	media_infos['video_codec'] = video_stream['codec_name']
	media_infos['frame_bitrate'] = format_info['bit_rate']
	frame_rate_num, frame_rate_den = video_stream['avg_frame_rate'].split('/')
	media_infos['frame_rate_num'] = frame_rate_num
	media_infos['frame_rate_den'] = frame_rate_den
	video_bitrate = video_stream['bit_rate']
	media_infos['video_bitrate'] = 0 if video_bitrate == "N/A" else video_bitrate

	## Profile
	video_profile = video_stream['profile']
	if video_profile == "High": video_profile = 3
	elif video_profile == "Medium": video_profile = 2
	elif video_profile == "Low": video_profile = 1
	else: video_profile = 0
	media_infos['video_profile'] = video_profile

	## Level and Resolution
	media_infos['video_level'] = video_stream['level']
	media_infos['resolutionX'] = video_stream['coded_width']
	media_infos['resolutionY'] = video_stream['coded_height']

	## Audio
	media_infos['audio_codec'] = audio_stream['codec_name']
	media_infos['audio_bitrate'] = audio_stream['bit_rate']
	media_infos['frequency'] = audio_stream['sample_rate']
	media_infos['channel'] = audio_stream['channels']

	## Duration
	media_infos['duration'] = format_info['duration'].split(".")[0]

	## Add only the modification Date (fix with SMB)
	date = datetime.fromtimestamp(os.path.getmtime(media_infos['path']))
	date = date.strftime('%Y-%m-%d %H:%M:%S')
	media_infos['date'] = date
	media_infos['mdate'] = date

	## UUID
	media_infos['fs_uuid'] = ""

	return media_infos
