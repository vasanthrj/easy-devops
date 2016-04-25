#! /usr/bin/env python
import propextractor
import Utils
import os
from optparse import OptionParser

paramFilePath=''
stackName = ''
keyPairParam = 'KeyPairParam'


def run():
	runTemplate()

def runTemplate():
	paramDict=propextractor.getParameterDict(paramFilePath)
	createKeyPair(paramDict)
	print "Creating stack"
	template = os.path.realpath(os.path.abspath(os.path.dirname(__file__))+ '/'  + '/sample.template')
	serverElbDnsParam = 'ServerElbDNS'
	propOutput=propextractor.readJsonFile(template, paramFilePath)
	command= "aws cloudformation create-stack --stack-name " + stackName + " --template-body file://" + template + " --parameters " + propOutput
	out=Utils.executeCommand(command)
	print "Command output :\n"+out
	Utils.cfnStackStatusPoll(stackName)
	print "Finished creating " + stackName + " stack"	
	outputKeyValue=Utils.getStackOutput(stackName)
	if outputKeyValue.has_key(serverElbDnsParam):
		paramdict = propextractor.getParameterDict(paramFilePath)
		paramdict[serverElbDnsParam]=outputKeyValue[serverElbDnsParam]
		propextractor.writeParamDictToJsonFile(paramdict, paramFilePath)


def createKeyPair(paramDict):
	print 'Server\'s ec2 key pair'
	if not paramDict.has_key(keyPairParam):
		print "Error: param " + keyPairParam + ' not found in parameter file'
		return
	fileStoreDir=os.path.realpath(os.path.abspath(os.path.dirname(__file__)))
	keyPairName = paramDict[keyPairParam]
	Utils.createEc2KeyPairIfNotPresent(keyPairName, fileStoreDir)


def main():
	defaultParamFilePath = os.path.realpath(os.path.abspath(os.path.dirname(__file__))+ '/'  + 'cfn-parameters.json')
	parser = OptionParser(usage="usage: %prog [options]")
	parser.add_option("-n", "--stackname", dest="stackName", default="sapmle-server", help="Server Stack name")
	parser.add_option("-p", "--paramfilepath", dest="paramFilePath", default=defaultParamFilePath, help="Cloudformation stack parameter file path. Default param file path: " + defaultParamFilePath)
	(options, args) = parser.parse_args()

	global stackName
	global paramFilePath
	stackName=options.__dict__['stackName']
	paramFilePath=os.path.abspath(options.__dict__['paramFilePath'])
	run()

main()
