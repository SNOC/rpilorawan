#!/usr/bin/python

## @package rpilora
#  This script allow the control of the rpilorawan expansion board for Raspberry Pi.
#
# 

import time
import serial
import sys
from time import sleep
import argparse

class RPIlora(object):
	portOpen = False
	verbosity = 1

	def __init__(self, port, verbosity):
		# allow serial port choice from parameter - default is /dev/ttyAMA0
		portName = port
		self.verbosity = verbosity
		
		if self.verbosity >= 2 : print 'Serial port : ' + portName
		self.ser = serial.Serial(
			port=portName,
			baudrate=57600,
			parity=serial.PARITY_NONE,
			stopbits=serial.STOPBITS_ONE,
			bytesize=serial.EIGHTBITS
		)

	def getc(self, size, timeout=1):
		return ser.read(size)

	def putc(self, data, timeout=1):
		ser.write(data)
		sleep(0.001) # give device time to prepare new buffer and start sending it

	def WaitFor(self, success, failure, timeOut):
		return self.ReceiveUntil(success, failure, timeOut) != ''

	def ReceiveUntil(self, success, failure, timeOut):
			iterCount = timeOut / 0.1
			self.ser.timeout = 0.1
			currentMsg = ''
			while iterCount >= 0 and success not in currentMsg and failure not in currentMsg :
				sleep(0.1)
				while self.ser.inWaiting() > 0 : # bunch of data ready for reading
						c = self.ser.read()
						currentMsg += c
				iterCount -= 1
			if success in currentMsg :
				return currentMsg
			elif failure in currentMsg :
				if self.verbosity >= 1 : print 'Failure (' + currentMsg.replace('\r\n', '') + ')'
			else :
				if self.verbosity >= 1 : print 'Receive timeout (' + currentMsg.replace('\r\n', '') + ')'
			return ''

	def open(self):
		if self.portOpen == False :
			if self.ser.isOpen() : # on some platforms the serial port needs to be closed first 
				if self.verbosity >= 2 : print('Serial port already open, closing it')
				self.ser.close()
			self.close()
			try:
				self.ser.open()
				if self.verbosity >= 2 : print('Serial port open')
			except serial.SerialException as e:
				sys.stderr.write("Could not open serial port {}: {}\n".format(ser.name, e))
				sys.exit(1)

			self.ser.write('sys get ver\r\n')
			if self.WaitFor('\r\n', 'ERROR', 3) :
				if self.verbosity >= 2 : print('Modem OK')
				self.portOpen = True
				return True
			else:
				if self.verbosity >= 1 : print 'Modem Error'
				self.ser.close()
				return False
		else:
			return True

	def sendCommand(self, message):
		if self.verbosity >= 2 : print 'Sending "' + message + '"'
		self.ser.write(message + "\r\n")
		rxData = self.ReceiveUntil('\r\n', 'ERROR', 5).replace('\r\n', '')
		if self.verbosity >= 2 : print 'Received "' + rxData + '"'
		return rxData

	def close(self):
		if self.ser.isOpen():
			self.ser.close()

if __name__ == '__main__':
	# --port <serial port path> --otaa devEUI appEUI AppKey --abp NwkSkey AppSKey devAddr --send <hex string> --receive --channel <channel>
	parser = argparse.ArgumentParser(description="Setup RPILora module connection and/or send data over configured LoRa network")
	group = parser.add_mutually_exclusive_group()
	group.add_argument("-o", "--otaa", nargs=3, help="over the air activation parameters <devEUI appEUI AppKey>")
	group.add_argument("-a", "--abp", nargs=3, help="activation by personnalization parameters <NwkSkey AppSKey devAddr>")
	parser.add_argument("-s", "--send", help="hex string encoded data to send")
	parser.add_argument("-r", "--receive", help="wait for downlink frame", action="store_true") # TODO: can not receive if no data sent
	parser.add_argument("-p", "--port", help="serial port path, defaults to /dev/ttyAMA0", default="/dev/ttyAMA0")
	parser.add_argument("-c", "--channel", type=int, choices=range(1, 223), help="LoRa channel, defaults to 1", default=1)
	parser.add_argument("-e", "--eui", help="get preprogrammed EUI", action="store_true")
	parser.add_argument("-v", "--verbosity", type=int, choices=range(0, 3), help="Verbosity, defaults to 1", default=1)
	args = parser.parse_args()
	
	errorCode = 0
	errorMessage = ''
	
	rpilora = RPIlora(args.port, args.verbosity)
	if args.eui:
		if rpilora.open() :
			received = rpilora.sendCommand('sys get hweui')
			print received
		else:
			errorCode = 12
	if args.otaa:
		if rpilora.open() :
			rpilora.sendCommand('sys reset')
			received = rpilora.sendCommand('mac set deveui ' + args.otaa[0])
			if received == 'ok':
				received = rpilora.sendCommand('mac set appeui ' + args.otaa[1])
				if received == 'ok':
					received = rpilora.sendCommand('mac set appkey ' + args.otaa[2])
					if received == 'ok':
						received = rpilora.sendCommand('mac join otaa')
						if received == 'ok':
							received = rpilora.ReceiveUntil('\r\n', 'ERROR', 20).replace('\r\n', '')
							if received == 'accepted':
								if rpilora.verbosity >= 1 : print 'join successful'
								received = rpilora.sendCommand('mac save')
								if received != 'ok':
									errorMessage = 'mac save failed: ' + received
									errorCode = 1
							else:
								errorMessage = 'mac join otaa failed: ' + received
								errorCode = 2
						else:
							errorMessage = 'mac join otaa failed: ' + received
							errorCode = 3
					else:
						errorMessage = 'mac set appkey failed: ' + received
						errorCode = 4
				else:
					errorMessage = 'mac set appeui failed: ' + received
					errorCode = 5
			else:
				errorMessage = 'mac set deveui failed: ' + received
				errorCode = 6
		else:
			errorCode = 12
	elif args.abp:
		if rpilora.open() :
			rpilora.sendCommand('sys reset')
			received = rpilora.sendCommand('mac set nwkskey ' + args.abp[0])
			if received == 'ok':
				received = rpilora.sendCommand('mac set appskey ' + args.abp[1])
				if received == 'ok':
					received = rpilora.sendCommand('mac set devaddr ' + args.abp[2])
					if received == 'ok':
						received = rpilora.sendCommand('mac join abp')
						if received == 'ok':
							received = rpilora.ReceiveUntil('\r\n', 'ERROR', 20).replace('\r\n', '')
							if received == 'accepted':
								if rpilora.verbosity >= 1 : print 'join successful'
								received = rpilora.sendCommand('mac save')
								if received is not 'ok':
									errorMessage = 'mac save failed: ' + received
									errorCode = 1
							else:
								errorMessage = 'mac join abp failed: ' + received
								errorCode = 7
						else:
							errorMessage = 'mac join abp failed: ' + received
							errorCode = 8
					else:
						errorMessage = 'mac set devaddr failed: ' + received
						errorCode = 9
				else:
					errorMessage = 'mac set appskey failed: ' + received
					errorCode = 10
			else:
				errorMessage = 'mac set nwkskey failed: ' + received
				errorCode = 11
		else:
			errorCode = 12
	if args.send:
		if rpilora.open() :
			command_string = 'mac tx '
			if not args.receive:
				command_string += 'un'
			command_string += 'cnf ' + str(args.channel) + ' ' + args.send
			received = rpilora.sendCommand(command_string)
			if received == 'ok':
				# send command syntax OK at this point
				if args.receive:
					# rx data present before mac_tx_ok
					loop_flag = True
					received_data = ""
					while loop_flag:
						received = rpilora.ReceiveUntil('\r\n', 'ERROR', 50).replace('\r\n', '')
						if received == 'mac_tx_ok':
							# we are done receiving
							if rpilora.verbosity == 0 :
								print received_data
							else:
								print 'RX data:' + received_data
							loop_flag = False
						elif received.startswith('mac_rx ', 0, 0):
							received_data += received.split()[2]
						else:
							loop_flag = False
							errorMessage = 'send failed: ' + received
							errorCode = 13
				else:
					received = rpilora.ReceiveUntil('\r\n', 'ERROR', 20).replace('\r\n', '')
					if received == 'mac_tx_ok':
						if rpilora.verbosity >= 1 : print 'Message sent'
					else:
						errorMessage = 'send failed: ' + received
						errorCode = 14
			else:
				errorMessage = command_string + ' failed: ' + received
				errorCode = 15
		
	
	rpilora.close()
	if rpilora.verbosity >= 1 and errorMessage != '' : print errorMessage
	sys.exit(errorCode)