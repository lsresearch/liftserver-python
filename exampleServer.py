#
# exampleServer.py
# LiftServer - Python
#
# Created by mkremer@lsr.com on 12/12/14
# Copyright (C) 2014 LSR
#
# This source file is licensed under the terms of The MIT License
# See LICENSE.txt for details
#

from flask import Flask, request, jsonify
app = Flask(__name__)

app.debug = True

import liftlib
from liftdebuggers import console
from liftstorage import fileSys

lift = liftlib.LiftLib(storage=fileSys.Storage('../test_liftstorage/'), debugger=console)

@app.route("/device-api/")
def default():
	return "Redirect to Python documentation?"

@app.route("/device-api/debug", methods=["POST", "PUT", "GET"])
def debug():
	print "DEBUG"
	print request.data
	return jsonify(**{
		'debug': 'gotit'
	})

@app.route("/device-api/rpc", methods=["POST", "PUT", "GET"])
def rpc():

	print request.headers
	print request.data

	if request.method == "PUT":
		transformResp = liftlib.getTransform(request, default="json")
		if transformResp['err']:
			print transformResp
			return jsonify(**transformResp)
		else:
			transform = transformResp['transform']
			keyResp = liftlib.getAccessKey(request)
			if keyResp['err']:
				data = transform.load(request, 'rpc')
				if "method" in data:
					if data["method"] == "GetAuthInfo":
						return transform.makeResponse({"jsonrpc": "2.0", 
							"result":{
								"deviceID": data["params"]["deviceId"],
								"registrationPin": "1234",
					 			"deviceKey": data["params"]["deviceId"], 
								"deviceSecret": "1234"
							},
							"id": data["id"]
						}, "rpc")
				return transform.makeResponse(transform.dump(keyResp, 'rpc'), 'rpc')
			else:
				key = keyResp['key']
				data = transform.load(request, 'rpc')
				rpcResp = lift.rpc(key, data)
				resp = transform.dump(rpcResp, 'rpc')
				print "Response: ", resp
				return transform.makeResponse(resp, 'rpc')
	else:
		print "ONLY PUT"
		return jsonify(**{
			'err': True,
			'code': 'You can only use PUT requests.'
		})

if __name__ == "__main__":
    app.run(port=3666, host="0.0.0.0")