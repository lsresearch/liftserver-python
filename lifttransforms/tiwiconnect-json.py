#
# tiwiconnect-json.py
# LiftServer - Python
#
# Created by mkremer@lsr.com on 12/12/14
# Copyright (C) 2014 LSR
#
# This source file is licensed under the terms of The MIT License
# See LICENSE.txt for details
#

from flask import jsonify
import simplejson

def load(value, url):
	return simplejson.loads(value.data)

def dump(value, url):
	return value

def makeResponse(value, url):
	return jsonify(**value)