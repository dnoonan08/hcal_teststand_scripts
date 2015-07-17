from hcal_teststand.register import *
from hcal_teststand.hcal_teststand import teststand
import sys
import random

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
	name = ""
	if len(sys.argv) == 1:
		name = "904"
	elif len(sys.argv) == 2:
		name = sys.argv[1]
	else:
		name = "904"
	ts = teststand(name)		# Initialize a teststand object. This object stores the teststand configuration and has a number of useful methods.

	result = [0]*24
	registers = [ 
		     register( ts , "HF1-10-iBot_CntrReg_CImode" , 1 ) , 
		     register( ts , "HF1-10-iBot_CntrReg" , 1 ) , 
		     register( ts , "HF1-10-iBot_LinkTestMode_BC0Enable" , 1 ) , 
		     register( ts , "HF1-10-iBot_LinkTestMode_Enable" , 1 ) , 
		     register( ts , "HF1-10-iBot_LinkTestMode" , 1 ) , 
		     register( ts , "HF1-10-iBot_LinkTestPattern" , 32 ) , 
		     register( ts , "HF1-10-iBot_scratch" , 32 ) , 
		     register( ts , "HF1-10-iTop_CntrReg_CImode" , 1 ) , 
		     register( ts , "HF1-10-iTop_CntrReg" , 1 ) , 
		     register( ts , "HF1-10-iTop_LinkTestMode_BC0Enable" , 1 ) , 
		     register( ts , "HF1-10-iTop_LinkTestMode_Enable" , 1 ) , 
		     register( ts , "HF1-10-iTop_LinkTestMode" , 1 ) , 
		     register( ts , "HF1-10-iTop_LinkTestPattern" , 32 ) , 
		     register( ts , "HF1-10-iTop_scratch" , 32 )
		     ]
	
	for i in range( 20 ) :

		for r in registers :
			r.setVerbosity( 0 )
		        value = getRandomValue( r.size )
			r.addTestToCache( value )

	for r in registers : 
		r.testCache()

# /MAIN

