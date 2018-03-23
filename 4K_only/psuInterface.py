# Tucker Elleflot

import prologixInterface 

pro = prologixInterface.prologixInterface()

class psuInterface:

	def __init__(self, gpibAddr, verbose=True):
		self.gpibAddr = gpibAddr
		self.verbose = verbose
		self.pro = pro

	def connGpib(self):
		self.pro.write('++addr ' + str(self.gpibAddr))

	def write(self, msg):
		self.connGpib()
		self.pro.write(msg)

	def read(self):
		return self.pro.read()

	def identify(self):
		self.write('*idn?')
		return self.read()

	def setChan(self, ch):
		self.write('inst:nsel ' + str(ch))

	def setVolt(self, ch, volt):
		self.setChan(ch)
		self.write('volt ' + str(volt))
		#if self.verbose:
		#	voltage = self.getVolt(ch)
			#print "CH " + str(ch) + " is set to " + str(voltage) " V"

	def setCurr(self, ch, curr):
		self.setChan(ch)
		self.write('curr ' + str(curr))
		#if self.verbose:
		#	current = self.getCurr(ch)
			#print "CH " + str(ch) + " is set to " + str(current) " A"

	def getVolt(self, ch):
		self.setChan(ch)
		self.write('volt?')
		voltage = float(self.read())
		return voltage

	def getCurr(self, ch):
		self.setChan(ch)
		self.write('curr?')
		current = float(self.read())
		return current

