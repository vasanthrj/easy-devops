#! /usr/bin/env python
import sys
import json
import subprocess
import time
import os

COMMAND_POLLING_INTERVAL_SEC=float(30)

def executeCommand(command):
	try:
		print "Executing command : " + command
		return subprocess.check_output(command, shell=True)
	except subprocess.CalledProcessError as grepexc:
		print "error code", grepexc.returncode, grepexc.output
		sys.exit("Error: Command failed.")

def describeCfnStack(stackName):
	command="aws cloudformation describe-stacks --stack-name " + stackName
	executeCommand(command)

def cfnStackStatusPoll(stackName):
	cfnStatusProcessList=['CREATE_IN_PROGRESS', 'UPDATE_IN_PROGRESS', 'UPDATE_COMPLETE_CLEANUP_IN_PROGRESS']
	cfnStatusCompletdList=['CREATE_COMPLETE', 'UPDATE_COMPLETE']
	stackStatus=''
	while True:
		command="aws cloudformation describe-stacks --stack-name " + stackName
		jsonOutput=executeCommand(command)
		try:
			jsondata = json.loads(jsonOutput)
			if jsondata.has_key('Stacks'):
				if len(jsondata['Stacks']) == 1:
					stackJson=jsondata['Stacks'][0]
					if stackJson.has_key('StackStatus'):
						stackStatus=stackJson['StackStatus']
					else:
						print "Stack json does not contain 'StackStatus'"
				else:
					print "Output json does not contain value for 'Stacks' key"
			else:
				print "Does not contain 'Stacks' key in output json"
		except ValueError, e:
			print "Error: Not a valid json: " + jsonOutput
		if stackStatus in cfnStatusProcessList:
			print "Stack create/update is in progress. AWS status code : " + stackStatus
			time.sleep(COMMAND_POLLING_INTERVAL_SEC)
			continue
		else:
			print "Finished stack create/update. Final AWS status code : " + stackStatus
			if stackStatus == 'ROLLBACK_IN_PROGRESS':
				print "Stack creation failed. Waiting for ROLLBACK_COMPLETE status"
				time.sleep(COMMAND_POLLING_INTERVAL_SEC)
				continue
			elif stackStatus == 'ROLLBACK_COMPLETE' or stackStatus == 'ROLLBACK_FAILED' or stackStatus in cfnStatusCompletdList :
				if stackStatus in cfnStatusCompletdList:
					print "Stack create/update completed successfully. AWS status code : " + stackStatus
					outputDict = getStackOutputFromJson(jsonOutput)
					if outputDict is not None:
						stackOutputFileName = stackName + "-stack-output.properties"
						print 'Stack\'s output is available in ' + stackOutputFileName
						stackOutputFileObj = open(stackOutputFileName, 'w')
						for key, value in outputDict.iteritems():
							tmpOutput = key + '=' + value
							stackOutputFileObj.write(tmpOutput)
							stackOutputFileObj.write("\n")
						stackOutputFileObj.close()

				print "Listing stack events and resources list to files"
				
				stackEventFileName = stackName + "-stack-event.json"
				stackEventCmd="aws cloudformation describe-stack-events --stack-name " + stackName
				stackEventOutput=executeCommand(stackEventCmd)
				stackEventFileObj = open(stackEventFileName, 'w')
				stackEventFileObj.write(stackEventOutput)
				stackEventFileObj.close()
				print "Stack events available in the file : " + stackEventFileName

				stackResourcesFileName =  stackName + "-stack-resources.json"
				stackResourcesCmd="aws cloudformation describe-stack-resources --stack-name " + stackName
				stackResourcesOutput = executeCommand(stackResourcesCmd)
				stackResourcesFileObj = open(stackResourcesFileName, 'w')
				stackResourcesFileObj.write(stackResourcesOutput)
				stackResourcesFileObj.close()
				print "Stack resource status available in the file : " + stackResourcesFileName
			break;

def getStackOutput(stackName):
	command='aws cloudformation describe-stacks --stack-name ' + stackName
	jsonOutput=executeCommand(command)
	return getStackOutputFromJson(jsonOutput)

def getStackOutputFromJson(jsonOutput):
	outputKeyValue={}
	try:
		jsondata = json.loads(jsonOutput)
		if jsondata.has_key('Stacks'):
			if len(jsondata['Stacks']) == 1:
				stackJson=jsondata['Stacks'][0]
				if stackJson.has_key('Outputs'):
					stackOutput=stackJson['Outputs']
					for index in range(len(stackOutput)):
						stackOutputItem=stackOutput[index]
						outputKey=stackOutput[index]['OutputKey']
						outputValue=stackOutput[index]['OutputValue']
						outputKeyValue[outputKey]=outputValue
				else:
					print "Stack json does not contain 'Outputs'"
			else:
				print "Output json does not contain value for 'Stacks' key"
		else:
			print "Does not contain 'Stacks' key in output json"
		return outputKeyValue
	except ValueError, e:
		print "Error: Not a valid json: " + jsonOutput


def createEc2KeyPairIfNotPresent(keyPairName, writeToFilePath):
	command  = 'aws ec2 create-key-pair --key-name ' + keyPairName
	try:
		print "Executing command : " + command
		jsonOutput = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
		print "Successfully created EC2 key pair : "+ keyPairName
		try:
			jsondata = json.loads(jsonOutput)
			if jsondata.has_key('KeyMaterial'):
				keyMaterial=jsondata['KeyMaterial']
				keyString = keyMaterial.replace("\\n","\n")
				keyPairFileName = os.path.join(writeToFilePath,keyPairName + '-' + getAccountNumber() + ".pem")
				with open(keyPairFileName, 'w') as keyPairFile:
					keyPairFile.write(keyString)
				print 'Written key pair contents to file : '+ keyPairFileName
		except ValueError, e:
			print "Error: Not a valid json: " + jsonOutput
	except subprocess.CalledProcessError as grepexc:
		if "Duplicate" in grepexc.output:
			print "Already created EC2 KeyPair : " + keyPairName
		else:
			print "error code", grepexc.returncode, grepexc.output

def getAccountNumber():
	command = 'aws ec2 describe-security-groups --query \'SecurityGroups[0].OwnerId\' --output text'
	try:
		accountId = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
		return accountId.strip()
	except subprocess.CalledProcessError as grepexc:
		print "error code", grepexc.returncode, grepexc.output
		return ''
