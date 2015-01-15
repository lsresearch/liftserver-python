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
app = Flask(__name__, static_url_path="")

app.debug = True

import liftlib, config, simplejson
from liftdebuggers import console
from liftstorage import fileSys

storage = fileSys.Storage(config.settings["database"]["directory"])
lift = liftlib.LiftLib(storage=storage, debugger=console)

@app.route("/")
def webapp():
	return app.send_static_file('index.html')

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

@app.route("/app-api/devices", methods=["GET"])
def app_devices_get():
	return jsonify(**{
		"devices": storage.getDevices()
	})

@app.route("/app-api/device/<id>", methods=["GET"])
def app_device_get(id):
	return jsonify(**{
		"device": storage.readDevice(id)
	})

@app.route("/app-api/devicetype", methods=["PUT"])
def app_add_devicetype():
	data = simplejson.loads(request.data)
	return jsonify(**{
		"data": storage.addDeviceType(data["name"], data["json"])
	})

@app.route("/app-api/devicetypes", methods=["GET"])
def app_get_devicetypes():
	return jsonify(**{
		"devicetypes": storage.getDeviceTypes()
	})

@app.route("/app-api/deletedevicetype", methods=["PUT"])
def app_delete_devicetype():
	return jsonify(**{
		"data": storage.deleteDeviceType(simplejson.loads(request.data)["id"])
	})

@app.route("/app-api/updatedevice", methods=["PUT"])
def app_update_device():
	return jsonify(**{
		"data": storage.updateDevice(simplejson.loads(request.data))
	})

@app.route("/app-api/purgeactions", methods=["PUT"])
def app_purgeactions():
	return jsonify(**{
		"data": storage.purgeAllAct(simplejson.loads(request.data)["id"])
	})

if __name__ == "__main__":
    app.run(port=config.settings["server"]["port"], host=config.settings["server"]["host"])