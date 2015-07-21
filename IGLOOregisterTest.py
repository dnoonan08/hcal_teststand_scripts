from hcal_teststand.register import *
from hcal_teststand.hcal_teststand import teststand
import sys
import random
from optparse import OptionParser
def getRandomValue( registerSize ) : 

	randomInt = random.randint(0,1)	
	for i in range( registerSize - 1 ) :
		if random.randint(0,1) : 
			randomInt = ( randomInt | 1 ) << 1
		else :
			randomInt = randomInt << 1
			
	return str(hex(randomInt))
		
# MAIN:
if __name__ == "__main__":
	parser=OptionParser()
	parser.add_option('-t','--teststand',dest='name',default='904',help="The name of the teststand you want to use (default is \"904\").")
	parser.add_option('-q','--qieid',dest='qieid',default='0x8D000000 0xAA24DA70',help="The ID of the QIE card we read.")
	(options, args) = parser.parse_args()
	ts = teststand(options.name)
	crateslot=ts.crate_slot_from_qie(qie_id=options.qieid)
	crate=crateslot[0]
	slot=crateslot[1]
	result = [0]*24
	registers = [ 
		     register( ts , "HF{0}-{1}-iBot_CntrReg_CImode".format(crate,slot) , 1 ) , 
		     register( ts , "HF{0}-{1}-iBot_CntrReg".format(crate,slot), 1 ) , 
		     register( ts , "HF{0}-{1}-iBot_LinkTestMode_BC0Enable".format(crate,slot), 1 ) , 
		     register( ts , "HF{0}-{1}-iBot_LinkTestMode_Enable".format(crate,slot) , 1 ) , 
		     register( ts , "HF{0}-{1}-iBot_LinkTestMode".format(crate,slot) , 1 ) , 
		     register( ts , "HF{0}-{1}-iBot_LinkTestPattern".format(crate,slot) , 32 ) , 
		     register( ts , "HF{0}-{1}-iBot_scratch".format(crate,slot) , 32 ) , 
		     register( ts , "HF{0}-{1}-iTop_CntrReg_CImode".format(crate,slot) , 1 ) , 
		     register( ts , "HF{0}-{1}-iTop_CntrReg".format(crate,slot) , 1 ) , 
		     register( ts , "HF{0}-{1}-iTop_LinkTestMode_BC0Enable".format(crate,slot) , 1 ) , 
		     register( ts , "HF{0}-{1}-iTop_LinkTestMode_Enable".format(crate,slot) , 1 ) , 
		     register( ts , "HF{0}-{1}-iTop_LinkTestMode".format(crate,slot) , 1 ) , 
		     register( ts , "HF{0}-{1}-iTop_LinkTestPattern".format(crate,slot) , 32 ) , 
		     register( ts , "HF{0}-{1}-iTop_scratch".format(crate,slot) , 32 )
		     ]
	
	for i in range( 20 ) :

		for r in registers :
			r.setVerbosity( 0 )
		        value = getRandomValue( r.size )
			r.addTestToCache( value )

	for r in registers : 
		r.testCache()

# /MAIN

