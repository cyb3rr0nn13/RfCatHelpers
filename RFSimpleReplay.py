#!/usr/bin/env python

import sys
from rflib import *
from struct import *
import bitstring
import operator
import argparse
import time
import pickle

parser = argparse.ArgumentParser(description='Dumb application to replay a signal',version="0.1-bricktop")
parser.add_argument('-f', action="store", default="433880000", dest="baseFreq",help='Target frequency to listen for remote (default 433880000)',type=int)
parser.add_argument('-r', action="store", dest="baudRate",default=4800,help='Baudrate, defaults to 4800',type=int)
parser.add_argument('-n', action="store", dest="numSignals",default=3,help='Number of signals to capture before replaying',type=int)
parser.add_argument('-i', action="store", default="24000", dest="chanWidth",help='Width of each channel (lowest being 24000 -- default)',type=int)
parser.add_argument('-o', action="store", default="", dest="outFile",help='output file to save to')
parser.add_argument('-p', action="store", default="20", dest="power",help='Power level for re-transmitting',type=int)
results = parser.parse_args()

rawCapture = [];
print "Configuring RfCat"
d = RfCat()
d.setMdmModulation(MOD_ASK_OOK)
d.setFreq(results.baseFreq)
d.setMdmSyncMode(0)
d.setMdmDRate(results.baudRate)
d.setMdmChanSpc(results.chanWidth)
d.setChannel(0)
d.setPower(results.power)
d.lowball(1)

print "Searching..."
while True:
	try:
		
		y, t = d.RFrecv(1)
		sampleString=y.encode('hex')
		#print sampleString
		strength= 0 - ord(str(d.getRSSI()))
		
		#sampleString = re.sub(r'((f)\2{8,})', '',sampleString)
		if (re.search(r'((0)\2{15,})', sampleString)):
			rawCapture.append(sampleString)
			print "Found " + str(sampleString)
			print "Signal Strength:" + str(strength)
			if(len(rawCapture) >= results.numSignals):
				break;
		
			
		
		
	except ChipconUsbTimeoutException:
		pass
	except KeyboardInterrupt:
		break
print "Saving phase"
outputCapture = rawCapture
if(results.outFile != ''):
	pickle.dump(outputCapture, open(results.outFile,"wb"))
print "Send Phase..."
#print rawCapture
emptykey = '\x00\x00\x00\x00\x00\x00\x00'
d.makePktFLEN(len(emptykey))
d.RFxmit(emptykey)
while True:
	try:
		freq = raw_input("Press <enter> to resend or type the frequency you wish to send on now:")
		if(freq != ''):
			d.setFreq(int(freq))
			
		for i in range(0,len(rawCapture)):
			key_packed = bitstring.BitArray(hex=rawCapture[i]).tobytes()
			#raw_input(" Press any key to send " + str(i+1) + " of " + str(len(rawCapture)))
			d.makePktFLEN(len(key_packed))
			d.RFxmit(key_packed)
			print "Sent " + str(i+1) + " of " + str(len(rawCapture))
	except KeyboardInterrupt:
		print "Bye!"
		d.setModeIDLE()
		sys.exit()
		break;
print "exiting."
d.setModeIDLE()