#
# liftlib.py
# LiftServer - Python
#
# Created by mkremer@lsr.com on 12/12/14
# Copyright (C) 2014 LSR
#
# This source file is licensed under the terms of The MIT License
# See LICENSE.txt for details
#

import os.path, pkgutil, lifttransforms, time

# The following code turns the lifttransforms inner modules into a dictionary that we can lookup transforms on

pkgpath = os.path.dirname(lifttransforms.__file__)
availableTransforms = [name for _, name, _ in pkgutil.iter_modules([pkgpath])]
transforms = {}

for transform in availableTransforms:
	transforms[transform] = __import__('lifttransforms.%s' % transform, globals(), locals(),['*'])

def getTransform(req, default=None):
	# "Errors" from this function must be handled by the route in the server.

	tName = req.headers.get("X-TC-Transform")

	if tName:
		if tName in transforms:
			return {
				'err': False,
				'transform': transforms[tName]
			}
		else:
			return {
				'err': True,
				'c': 2003,
				'errMsg': "Transform doesn't exist."
			}
	else:
		if default:
			return {
				'err': False,
				'transform': transforms[default]
			}
		else:
			return {
				'err': True,
				'c': 2003,
				'errMsg': "No transform sent."
			}

def getAccessKey(req):

	key = req.headers.get("X-TC-Key")

	if key:
		return {
			'err': False,
			'key': key
		}
	else:
		return {
			'err': True,
			'c': 2000,
			'errMsg': "No access key sent."
		}

class LiftLib(object):

	def __init__(self, storage=None, debugger=None):
		if str(type(storage)) == "<type 'module'>":
			self.Storage = storage.Storage()
		else:
			self.Storage = storage
		if str(type(debugger)) == "<type 'module'>":
			self.Debugger = debugger.Debugger()
		else:
			self.Debugger = debugger

	def debug(self, m):
		if self.Debugger:
			self.Debugger.output(m)

	def rpc(self, key, data):
		
		if "id" in data:
			respid = data["id"]
		else:
			respid = ""

		resp = {
			"jsonrpc": "2.0",
			"id": respid,
			"result": {}
		}

		# ack an Action if set
		if "params" in data:
			if "aID" in data["params"]:
				self.Storage.ackAct(key, data["params"]["aID"])

		if "method" in data:

			if data["method"] == "SetAtts":
				for profile, attributes in data["params"].iteritems():
					if profile != "aID":
						for att, val in attributes.iteritems():
							self.Storage.setAtt(key, profile, att, val)

			if data["method"] == "GetAtts":
				if "params" not in data:
					# We're getting all of the attributes
					resp["result"] = self.Storage.getAllAtts(key)
				else:
					# Only get specific atts
					for profile, attributes in data["params"].iteritems():
						if profile != "aID":
							resp["result"][profile] = {}
							for att in attributes:
								check = self.Storage.getAtt(key, profile, att)
								if check["err"] == False:
									resp["result"][profile][att] = check["value"]
								else:
									self.debug("Att not found")
									self.debug(check)

			if data["method"] == "GetAct":
				check = self.Storage.getNextAct(key)
				if check['err'] == False:
					resp["result"]["aID"] = check["value"]["aID"]
					resp["result"]["action"] = check["value"]
					del resp["result"]["action"]["aID"]
				else:
					self.debug("No action found")
					self.debug(check)

			if data["method"] == "CreateAct":
				self.Storage.createAct(key, data["params"]["profile"], data["params"]["action"], data["params"]["arguments"])

		resp["result"]["aCnt"] = self.Storage.getActCount(key)

		return resp
