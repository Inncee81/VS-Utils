import os, argparse, urllib, urllib2, logging
from parse import parse_cfg, synoindex_modes

## Parse the config
config_file = os.path.dirname(os.path.abspath(__file__)) + '/config.txt'
cfg = parse_cfg(config_file, "client")

## Setup the client logging file
client_log = "%s/%s" % (cfg.client_logs, "client.log")
logging.basicConfig(filename=client_log, filemode='a',
					format='%(asctime)s - %(levelname)s: %(message)s')

## Set the logger and its level
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

### Synoindex-Client
def client():

	args = argparse.Namespace()
	parser = argparse.ArgumentParser(description='SynoIndex-Client')
	parser.add_argument('-o','--option', required=True,
						help='Option for synoindex')
	parser.add_argument('-f','--filepath', required=True,
						help='file path argument for synoindex')
	args = parser.parse_args()

	## Read config file
	config_file = os.path.dirname(os.path.abspath(__file__)) + '/config.txt'
	cfg = parse_cfg(config_file, "client")

	## Validation of the arguments
	if(args.option not in synoindex_modes):
		logger.error("Passed option not supported"); exit()
	if not os.path.exists(args.filepath):
		logger.error("Passed file does not exist"); exit()

	## Call the url and get the answer of the server
	query_vars = {'option': args.option, 'filepath': args.filepath}
	url = "%s/synoindex?" % cfg.url
	url = url + urllib.urlencode(query_vars)
	logger.debug(url)
	contents = urllib2.urlopen(url).read()
	logger.debug(contents)

if __name__ == "__main__":
	client()