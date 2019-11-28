'''
This module provides some helpers in order to manipulate Enhanced ShockBurst packets.
'''
def frequencyToChannel(frequency):
	'''
	This function converts a frequency to the corresponding Enhanced ShockBurst channel.
	
	:param frequency: frequency to convert (MHz)
	:type frequency: int
	:return: channel associated to the provided frequency
	:rtype: int

	:Example:

		>>> frequencyToChannel(2420)
		20
		>>> frequencyToChannel(2402)
		02

	'''
	channel = int(frequency) - 2400
	return channel

def channelToFrequency(channel):
	'''
	This function converts an Enhanced ShockBurst channel to the corresponding frequency.
	
	:param channel: ESB channel to convert
	:type channel: int
	:return: corresponding frequency (MHz)
	:rtype: int

	:Example:

		>>> channelToFrequency(37)
		2437
		>>> channelToFrequency(8)
		2408

	'''
	freqOffset = channel
	return 2400 + freqOffset

def bytes2bits(data):
	'''
	This function converts bytes to the corresponding bits sequence (as string).
	
	:param data: bytes to convert
	:type data: bytes
	:return: corresponding bits sequence
	:rtype: str

	:Example:

		>>> bytes2bits(b"\x01\x02\x03\xFF")
		'00000001000000100000001111111111'
		>>> bytes2bits(b"ABC")
		'010000010100001001000011'

	'''
	return "".join(["{:08b}".format(i) for i in bytes(data)])

def bits2bytes(bits):
	'''
	This function converts a sequence of bits (as string) to the corresponding bytes.

	:param bits: string indicating a sequence of bits (e.g. "10110011")
	:type bits: str
	:return: corresponding bytes
	:rtype: bytes

	:Example:

		>>> bits2bytes('00000001000000100000001111111111')
		b'\x01\x02\x03\xff'
		>>> bits2bytes('010000010100001001000011')
		b'ABC'
		
	'''
	return bytes([int(j+((8-len(j))*"0"),2) for j in [bits[i:i + 8] for i in range(0, len(bits), 8)]])

def bitwiseXor(a,b):
	'''
	This function returns the result of a bitwise XOR operation applied to two sequences of bits (a and b);

	:param a: string indicating a sequence of bits (e.g. "10101010")
	:type a: str
	:param b: string indicating a sequence of bits (e.g. "10101010")
	:type b: str
	:return: result of the XOR operation
	:rtype: str

	:Example:

		>>> bitwiseXor('11001111','10101010')
		'01100101'
		>>> bitwiseXor('11111111','00101010')
		'11010101'
		>>> bitwiseXor('11111111','11001100')
		'00110011'
	
	'''
	if len(a) != len(b):
		return None
	result = ""
	for i in range(len(a)):
		valA = a[i] == "1"
		valB = b[i] == "1"
		result += "1" if valA ^ valB else "0"
	return result


def calcCrcByte(crc,byte,bits):
	'''
	This function calculates the temporary value generated by an iteration of CRC calculation.
	
	:param crc: previous temporary value of CRC
	:type crc: bytes
	:param byte: byte to use in the current iteration
	:type byte: bytes
	:param bits: number of bits of the byte to take into account in the calculation
	:type bits: int
	
	'''
	polynome = bytes2bits(b'\x10\x21')
	crc_ba = bytes2bits(crc)
	byte_ba = bytes2bits(bytes([byte]))
	crc_ba = bitwiseXor(crc_ba,byte_ba + "00000000")
	while bits>0:
		bits-=1
		if crc_ba[0:1] == '1':
			crc_ba = crc_ba[1:]+'0'				
			crc_ba = bitwiseXor(crc_ba,polynome)
		else:
			crc_ba = crc_ba[1:]+'0'
	return bits2bytes(crc_ba)

def calcCrc(packet):
	'''
	This function calculates the CRC of an Enhanced Shockburst packet.

	:param packet: raw bytes of packet (without CRC and preamble)
	:type packet: bytes
	:return: calculated CRC
	:rtype: bytes

	:Example:

		>>> calcCrc(bytes.fromhex('e846f92fa429006100007f57ff80004900')).hex()
		'9ed4'

	'''
	crc = b"\xFF\xFF"
	for x in packet[:-1]:
		crc = calcCrcByte(crc,x,8)
	crc = calcCrcByte(crc, packet[-1],1)
	return crc