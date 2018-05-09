import socket as socket

ip = '192.168.1.8'
escapeString = 'xYzZyX'

class prologixInterface:

	def __init__(self, ip=ip, escapeString=escapeString):
		self.ip = ip
		self.escapeString = escapeString
		#self.gpibAddr = gpibAddr
		self.connSocket()
		self.configure()

#	def connSocket(self):
#		attempts = 0
#		while attempts < 5:
#			try:
#				self.pro = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#				self.pro.settimeout(1)
#				self.pro.connect((ip, 1234))
#			except socket.timeout:
#				print 'timeout, trying again'
#				attempts += 1

	def connSocket(self):
		self.pro = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.pro.connect((ip, 1234))
		#
		self.pro.settimeout(5)
	
	def configure(self):
		self.write('++mode 1\n')
		self.write('++auto 1\n')
		#self.write('++addr ' + str(self.gpibAddr))

	def write(self, msg):
		self.pro.send(msg + '\n')

	def writeGpib(self, gpibAddr, msg):
		self.write('++addr ' + str(gpibAddr))		
		self.write(msg)

	def read(self):
		return self.pro.recv(128).rstrip('\n').rstrip('\r')

	def identify(self):
		self.write('++ver')
		return self.read()
