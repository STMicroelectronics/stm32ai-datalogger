###################################################################################
#   Copyright (c) 2020-2021 STMicroelectronics.
#   All rights reserved.
#   This software is licensed under terms that can be found in the LICENSE file in
#   the root directory of this software component.
#   If no LICENSE file comes with this software, it is provided AS-IS.
###################################################################################

__author__ = "Romain LE DONGE"
__copyright__ = "Copyright (c) 2021 STMicroelectronics"
__license__ = """
    Copyright (c) 2020-2021 STMicroelectronics.
    All rights reserved.
    This software is licensed under terms that can be found in the LICENSE file in
    the root directory of this software component.
    If no LICENSE file comes with this software, it is provided AS-IS.
"""


from ai_logging.core import DriverInterface
from ai_logging.core.exceptions import *
import usb

class UsbWcidDriver(DriverInterface):
	def __init__(self, *args, **kwargs):
		self.device = None
		self.write_chunk_size = 512

	def connect(self, *args, **kwargs):
		""" Connect to the device
		Arguments: 
			'vidpid' specified as first parameter or as named parameter
		"""

		vidpid = None
		if 'vidpid' in kwargs:
			vidpid = kwargs['vidpid']
		else:
			if len(args) > 0:
				vidpid = args[0]

		if vidpid is None:
			raise ConnectionException("Error: can't connect, argument 'vidpid' must be explicitely indicated or passed as argument")

		usb_connection_info = vidpid.split(':')
		if len(usb_connection_info) != 2:
			print("Error: can't connect with {}, must be VID:PID".format(vidpid))
			self.device = None
			raise ConnectionException("Error: can't connect, argument 'vidpid' must be explicitely indicated or passed as argument")

		self.device = usb.core.find(idVendor=int(usb_connection_info[0], 16), 
			idProduct=int(usb_connection_info[1], 16)) 


	def byte_available(self, *args, **kwargs):
		return 128 # This is a HACK, libusb is unable to return how many packet are present in the buffer


	def read(self, nb_byte, *args, **kwargs):
		"""
		Argument: 
			'endpoint' must be specified as named parameter or as second parameter
		"""
		endpoint = None
		if 'read_endpoint' in kwargs:
			endpoint = kwargs['read_endpoint']
		else:
			if len(args) >= 2:
				endpoint = args[1]
		
		if endpoint is None:
			raise ReadException("Error: can't read, 'endpoint' must be specified as named parameter or as second parameter")

		if self.device is None:
			raise ReadException("Error: can't read, internal device is not initialized")

		try:
			if isinstance(endpoint, str):
				endpoint = int(endpoint, 16)
			
			data_read = self.device.read(endpoint, nb_byte, timeout=5000)
			byte_data = b''.join([bytes.fromhex(hex(x)[2:].zfill(2)) for x in data_read])
			return byte_data
		except usb.core.USBError as e:
			print("Error while reading: {}".format(e))
			return b''
		
	def write(self, data:bytes, *args, **kwargs):
		endpoint = None
		if 'write_endpoint' in kwargs:
			endpoint = kwargs['write_endpoint']
		else:
			if len(args) >= 2:
				endpoint = args[1]

		if endpoint is None:
			raise ReadException("Error: can't read, 'endpoint' must be specified as named parameter or as second parameter")

		if self.device is None:
			print("Attempting to write to None device")
			return
		
		bytes_written = 0
		bytes_left = len(data)
		while bytes_left > 0:
			a = self.device.write(endpoint, data[bytes_written:bytes_written+self.write_chunk_size], timeout=5000)
			bytes_left -= a
			bytes_written += a

		return bytes_written

	def close(self, *args, **kwargs):	
		if self.device is not None:
			self.device.reset()
		self.device = None
	
	def is_connected(self, *args, **kwargs):
		if self.device is None:
			return False
		else:
			return True


def test_libusb():
	import usb.core

	usb.core.show_devices()

	dev = usb.core.find(idVendor=0x0483, idProduct=0x5743) # Try without parameter also
	#dev = usb.core.find(idVendor=0x0458, idProduct=0x003A)
	#dev = usb.core.find(idVendor=0x0C76, idProduct=0x161F)
	print(dev)
	dev.reset() # Remove other processes that are attached to the USB
	dev.set_configuration() # This will enable the default I don't know what

	cfg = dev.get_active_configuration()
	intf = cfg[(0,0)] # Fetching interface
	eps = intf.endpoints() # Get all endpoints
	print("EPS:",eps)

	#ep = eps[0]
	#ep = usb.util.find_descriptor(intf, custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT)
	#ep.write('toto')

	#dev.write(0x01, 'gaga')
	try:
		dev.read(0x81, 100, timeout=2000)
	except Exception as e:
		print(e)

	try:
		dev.read(0x82, 100, timeout=2000)
	except Exception as e:
		print(e)

	try:
		dev.read(0x83, 100, timeout=2000)
	except Exception as e:
		print(e)

	try:
		dev.read(0x84, 100, timeout=2000)
	except Exception as e:
		print(e)

	try:
		dev.read(0x85, 100, timeout=2000)
	except Exception as e:
		print(e)


if __name__ == '__main__':
	test_libusb()

