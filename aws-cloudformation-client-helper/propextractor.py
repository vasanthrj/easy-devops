#! /usr/bin/env python
import sys
import json
from collections import OrderedDict

CONSTANT_PARAMETERS = 'Parameters'
CONSTANT_PARAMETER_VALUE = 'ParameterValue'
CONSTANT_PARAMETER_KEY = 'ParameterKey'

def readJsonFile(jsonFile, parametersFile):
	try:
		jsonFileObj = open(jsonFile)
		try:
			validJsonData = json.loads(jsonFileObj.read())
			if isContainParameterKeyInJson(validJsonData):
				requiredkeyList = readCfnProperties(validJsonData)
				if len(requiredkeyList) > 0:
					paramsDict = getParameterDict(parametersFile)
					return buildCfnParameters(requiredkeyList, paramsDict)
		except ValueError, e:
			sys.exit("Error: Not a valid json: " + jsonFile)
		jsonFileObj.close()
	except IOError:
		raise IOError, "Error: can\'t find file or read data" + jsonFile

def buildCfnParameters(requiredkeyList, paramsDict):
	outputString = ''
	for key in requiredkeyList:
		if key in paramsDict:
			value = paramsDict[key]
			if ',' in value:
				value = "\"" + value + "\""
			outputString = outputString + "'" + CONSTANT_PARAMETER_KEY + '=' + key + ',' + CONSTANT_PARAMETER_VALUE + '=' + value + "'"
		else:
			sys.exit("Error: Parameter " + key + " does not exists in parameters file")
		outputString = outputString + ' '
	return outputString

def getParameterDict(parametersFile):
	try: 
		paramJsonFileObj = open(parametersFile)
		try:
			paramJsonData = json.loads(paramJsonFileObj.read())
			parameterDict = OrderedDict()
			for params in paramJsonData:
				paramKey = ''
				paramValue = ''
				for key, value in params.iteritems():
					if key == CONSTANT_PARAMETER_KEY:
						paramKey = value
					elif key == CONSTANT_PARAMETER_VALUE:
						paramValue = value
				parameterDict[paramKey] = paramValue
			return parameterDict
		except ValueError, e:
			sys.exit("Parameter file is not a valid json: " + parametersFile)
	except IOError:
		sys.exit("Error: can\'t find file or read data" + parametersFile)


def isContainParameterKeyInJson(jsonData):
	for key, value in jsonData.iteritems():
		if key == CONSTANT_PARAMETERS:
			return 1
	return 0

def readCfnProperties(jsonData):
	keyList = [];
	for key, value in jsonData['Parameters'].iteritems():
		keyList.append(key)
	return keyList

def getParameterFromFile(paramFile, paramName):
	try: 
		paramJsonFileObj = open(paramFile)
		try:
			paramJsonData = json.loads(paramJsonFileObj.read())
			parameterDict = {};
			for params in paramJsonData:
				paramKey = ''
				paramValue = ''
				for key, value in params.iteritems():
					if key == CONSTANT_PARAMETER_KEY:
						paramKey = value
					elif key == CONSTANT_PARAMETER_VALUE:
						paramValue = value
				if paramKey == paramName:
					return paramValue
			return None
		except ValueError, e:
			sys.exit("Parameter file is not a valid json: " + parametersFile)
	except IOError:
		sys.exit("Error: can\'t find file or read data" + parametersFile)

def writeParamDictToJsonFile(paramsDict, paramFile):
	reponse=[]
	for key,value in paramsDict.iteritems():
		item=OrderedDict()
		item['ParameterKey'] = key
		item['ParameterValue'] = value
		reponse.append(item)
	with open(paramFile, 'w') as outfile:
		json.dump(reponse, outfile, indent=4)
