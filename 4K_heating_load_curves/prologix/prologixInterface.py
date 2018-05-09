import socket as s

ip = '192.168.1.8'
escapeString = 'xYzZyX'

class prologixInterface():

    def __init__(self):
        self.ip = ip
        self.escapeString = escapeString
        self.prologix = self.connSocket()
        self.verbose = True
        GPIBid = self.getGPIBdevID()
        print 'Current GPIB instrument: ' + GPIBid.split(',')[0] + GPIBid.split(',')[1]
        print 'Current device ID: ' + GPIBid.split(',')[2]
        print 'Keithely 9100433 = GPIB-1\nKeithely 9010709 = GPIB-2\nKeithley 9102893 = GPIB-3'

    def connSocket(self):
        prologix = s.socket(s.AF_INET, s.SOCK_STREAM)
        prologix.connect((ip, 1234))
        prologix.send('++ver\n')
        print prologix.recv(128)
        prologix.send('++mode 1\n')
        prologix.send('++mode\n')
        mode = prologix.recv(128)
        print 'Auto mode:' + mode
        n = prologix.send('++auto 1\n')
        return prologix

    def readPrologix(self):
        return self.prologix.recv(128).rstrip('\n')

    def connGPIBaddr(self, GPIBaddr):
        self.prologix.send('++addr ' + str(GPIBaddr) + '\n')
        GPIBid = self.getGPIBdevID()
        channel = self.getKeithActiveChannel()
        print 'Connected to GPIB-' + str(GPIBaddr)
        print GPIBid
        print 'Active channel: ' + channel

    def writeGPIB(self, msg):
        self.prologix.send(msg + '\n')

    def getGPIBdevID(self):
        self.writeGPIB('*IDN?')
        return self.readPrologix()

    def getKeithActiveChannel(self):
        self.writeGPIB('INST:SEL?\n')
        return self.readPrologix()

    def setKeithChannel(self, channel):
        self.writeGPIB('INST:SEL CH' + str(channel))
        self.keithActiveChannel = channel
        if self.verbose == True:
            print self.getKeithActiveChannel(), 'is active'

    def toggleKeithOutput(self, state):  # state: 1 = 'on', 0 = 'off'
        self.writeGPIB('OUTP ' + str(state))

    def getKeithVolt(self, channel):
        self.writeGPIB('MEAS:VOLT? CH' + str(channel))
        return self.readPrologix()

    def getKeithCurrent(self, channel):
        if channel == 'ALL':
            self.writeGPIB('MEAS:CURR? ALL')
        else:
            self.writeGPIB('MEAS:CURR? CH' + str(channel))
        return self.readPrologix()

    def setKeithVolt(self, v):
        self.writeGPIB('VOLT ' + str(v))
#        print 'CH', self.keithActiveChannel, '=', str(v), 'V'

    def setKeithCurrent(self, i):
        self.writeGPIB('CURR ' + str(i))
        print 'CH', self.KeithActiveChannel, '=', str(i), 'A'
