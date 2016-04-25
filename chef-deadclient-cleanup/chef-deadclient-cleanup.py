#! /usr/bin/env python
from datetime import datetime
import subprocess
import sys
import logging
import logging.handlers

def main(arg):
	timeoutMinutes = 0
	knifeConf = ''
	logger = logging.getLogger("chefserver-cleanupclient")
	logger.setLevel(logging.INFO)
	LOG_FILENAME = '/var/log/chefserver-cleanup.log'
	handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=10485760, backupCount=1)
	formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
	handler.setFormatter(formatter)
	logger.addHandler(handler)

	logger.info("Staring chef server cleanup tool")
	if len(arg) < 3:
		logger.error("Error: " + "Required inactive client check time in minute and knife conf file. chefserver-cleanup.py 5 /etc/chef/knife.rb")
		sys.exit(1)
	knifeConf = arg[2]
	try:
		timeoutMinutes = int(arg[1])
	except ValueError:
		print("Input argument is not integer.")

	knifeCmd = subprocess.Popen(["knife exec -E 'nodes.all {|n| puts \"#{n.name} #{Time.at(n[:ohai_time])}\"}\' -c " + knifeConf ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	out, err = knifeCmd.communicate()
	for entry in out.strip().split('\n'):
		entrylist = entry.strip().split(' ')
		if len(entrylist) == 4:
			time = entrylist[1] + ' ' + entrylist[2]
			dt = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
			difftime = datetime.today() - dt
			totalminutes = ((difftime.microseconds + (difftime.seconds + difftime.days * 24 * 3600) * 10**6) / 10**6)/60
			if totalminutes > timeoutMinutes:
				clientname = entrylist[0]
				logger.info("Delete client : " +clientname)
				deleteClient = subprocess.Popen(["knife client delete " +  clientname + " -y -c "+ knifeConf ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
				clientout, clienterr = deleteClient.communicate()
				if len(clientout.strip()) > 0:
					logger.info(clientout.strip())
				if len(clienterr.strip()) > 0:
					logger.error(clienterr.strip())
				logger.info("Delete node : " + clientname)
				deleteNode = subprocess.Popen(["knife node delete " + clientname + " -y -c "+ knifeConf ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                                nodeout, nodeerr = deleteNode.communicate()
                                if len(nodeout.strip()) > 0:
                                        logger.info(nodeout.strip())
                                if len(nodeerr.strip()) > 0:
                                        logger.error(nodeerr.strip())
	logger.info("Finished chef server cleanup tool")

main(sys.argv)