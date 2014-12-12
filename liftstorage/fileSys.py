#
# fileSys.py
# LiftServer - Python
#
# Created by mkremer@lsr.com on 12/12/14
# Copyright (C) 2014 LSR
#
# This source file is licensed under the terms of The MIT License
# See LICENSE.txt for details
#

import os, time, simplejson

class Storage(object):

	def __init__(self, root=None):
		self.root = root
		if not os.path.exists(self.root):
			os.makedirs(self.root)

	def readDevice(self, accessKey):
		if not os.path.exists(self.root+accessKey+'.json'):
			return simplejson.loads('{"attributes": {}, "actions": [], "onAction": 0}')
		f = open(self.root+accessKey+'.json', 'rb+')
		v = f.read()
		f.close()
		if v == "":
			return simplejson.loads('{"attributes": {}, "actions": [], "onAction": 0}')
		return simplejson.loads(v)

	def writeDevice(self, accessKey, value):
		f = open(self.root+accessKey+'.json', 'w')
		f.write(simplejson.dumps(value))
		f.close()

	def ensureProfile(self, data, profile):
		if profile not in data["attributes"]:
			data["attributes"][profile] = {}
		return data

	def setAtt(self, accessKey, profile, att, value, timestamp=None):
		data = self.readDevice(accessKey)
		data = self.ensureProfile(data, profile)
		data["attributes"][profile][att] = value
		if not timestamp:
			timestamp = str(time.time())
		f = open(self.root+accessKey+'.'+str(profile)+'.'+str(att)+'.log','a')
		f.write('[%s] %s\n' % (timestamp, str(value)))
		f.close()
		self.writeDevice(accessKey, data)

	def getAtt(self, accessKey, profile, att):
		data = self.readDevice(accessKey)
		data = self.ensureProfile(data, profile)
		if att in data["attributes"][profile]:
			return {
				"err": False,
				"value": data["attributes"][profile][att]
			}
		else:
			return {
				"err": True
			}

	def getAllAtts(self, accessKey):
		data = self.readDevice(accessKey)
		return data["attributes"]

	def createAct(self, accessKey, profile, action, arguments):
		data = self.readDevice(accessKey)
		data["actions"].append({
			"aID": data["onAction"],
			profile: {
				action: arguments
			}
		})
		data["onAction"] = data["onAction"] + 1
		self.writeDevice(accessKey, data)

	def getNextAct(self, accessKey):
		data = self.readDevice(accessKey)
		if len(data["actions"]) != 0:
			return {
				"err": False,
				"value": data["actions"][0]
			}
		else:
			return {
				"err": True
			}

	def ackAct(self, accessKey, aID):
		data = self.readDevice(accessKey)
		if aID == "force" or aID == "FORCE":
			if len(data["actions"]) > 0:
				del data["actions"][0]
		else:
			for i in range(0,len(data["actions"])):
				if data["actions"][i]["aID"] == aID:
					del data["actions"][i]
					break
		self.writeDevice(accessKey, data)


	def getActCount(self, accessKey):
		data = self.readDevice(accessKey)
		return len(data["actions"])


