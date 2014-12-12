import struct, binascii

def load(value):

	contentLength = value.headers.get("Content-Length")

	packed_data = value.body

	msgIdLenStruct = struct.Struct('B')
	unpacked_msgIdLen = msgIdLenStruct.unpack(packed_data[0])[0] # Automatically did [0] here to get the len stored

	if unpacked_msgIdLen == 0:
		formatString = 'B '+str(contentLength - 1)+'s'
		allStruct = struct.Struct(formatString)
		unpacked_all = allStruct.unpack(packed_data)

		attributeValue = binascii.hexlify(unpacked_all[1])

		res = {
			"setAtts": [
				{
					"attidx": "bin",
					"attv": [{"v": attributeValue}]
				}
			]
		}

	else:
		formatString = 'B ' + str(unpacked_msgIdLen) + 's ' + str(contentLength - unpacked_msgIdLen - 1) + 's'
		allStruct = struct.Struct(formatString)
		unpacked_all = allStruct.unpack(packed_data)

		ackValue = unpacked_all[1]
		if ackValue == "\x7f":
			ackValue = "force"

		attributeValue = binascii.hexlify(unpacked_all[2])

		res = {
			"ma": ackValue,
			"setAtts": [
				{
					"attidx": "bin",
					"attv": [{"v": attributeValue}]
				}
			]
		}

	return res

def dump(value):
	return value

def makeResponse(value):
	return jsonify(**value)