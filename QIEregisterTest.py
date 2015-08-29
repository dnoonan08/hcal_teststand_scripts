from hcal_teststand.register import *
from hcal_teststand.hcal_teststand import teststand
import sys
import random

# VARIABLES:
fe_crate = 1
fe_slot = 10
register_names = []
for i_qie in range(1, 25):
	register_names.extend([
		"HF{0}-{1}-QIE{2}_CalMode".format(fe_crate, fe_slot, i_qie),
		"HF{0}-{1}-QIE{2}_ChargeInjectDAC".format(fe_crate, fe_slot, i_qie),
		"HF{0}-{1}-QIE{2}_Lvds".format(fe_crate, fe_slot, i_qie),
		"HF{0}-{1}-QIE{2}_TGain".format(fe_crate, fe_slot, i_qie),
		"HF{0}-{1}-QIE{2}_CapID0pedestal".format(fe_crate, fe_slot, i_qie),
		"HF{0}-{1}-QIE{2}_CkOutEn".format(fe_crate, fe_slot, i_qie),
		"HF{0}-{1}-QIE{2}_PedestalDAC".format(fe_crate, fe_slot, i_qie),
		"HF{0}-{1}-QIE{2}_TimingIref".format(fe_crate, fe_slot, i_qie),
		"HF{0}-{1}-QIE{2}_CapID1pedestal".format(fe_crate, fe_slot, i_qie),
		"HF{0}-{1}-QIE{2}_DiscOn".format(fe_crate, fe_slot, i_qie),
		"HF{0}-{1}-QIE{2}_RangeSet".format(fe_crate, fe_slot, i_qie),
		"HF{0}-{1}-QIE{2}_TimingThresholdDAC".format(fe_crate, fe_slot, i_qie),
		"HF{0}-{1}-QIE{2}_CapID2pedestal".format(fe_crate, fe_slot, i_qie),
		"HF{0}-{1}-QIE{2}_FixRange".format(fe_crate, fe_slot, i_qie),
		"HF{0}-{1}-QIE{2}_RinSel".format(fe_crate, fe_slot, i_qie),
		"HF{0}-{1}-QIE{2}_Trim".format(fe_crate, fe_slot, i_qie),
		"HF{0}-{1}-QIE{2}_CapID3pedestal".format(fe_crate, fe_slot, i_qie),
		"HF{0}-{1}-QIE{2}_Idcset".format(fe_crate, fe_slot, i_qie),
		"HF{0}-{1}-QIE{2}_TDCMode".format(fe_crate, fe_slot, i_qie),
	])
# /VARIABLES

# FUNCTIONS:
def getRandomValue( ) : 

	### 
	# the 47 should not be hardcoded and should instead
	# be taken from register.size.  However, this needs to 
	# be done carefully so taht the bits are divided up
	# into 24 bit chunks correctly...
	###
	randomInt = random.randint(0,1)	
	for i in range( 47 ) :
		if random.randint(0,1) : 
			randomInt = ( randomInt | 1 ) << 1
		else :
			randomInt = randomInt << 1
			
	return str(hex(randomInt))
		
def testRandomValue( register ):

	randomValue = getRandomValue()

	testValues = [ randomValue[0:8] , 
		       '0x'+randomValue[8:16]
		       ]

	#print "testing:",testValues
        value = ''
        register.write(testValues[1]+" "+testValues[0])
        value = register.read()

	if value.find("ERROR") != -1 : 
		print "ERROR in results"
		return False

        values = value.split("'")[1].split()
	#print "result:",values
	if values == testValues : 
		return True
	else : 
		return False 
# /FUNCTIONS

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
	registers = []
	for name in register_names:
		registers.append(register(ts, name, 48))		# HERE on "48"

	for i in range( 5 ) :
		#print "test",i
		for r in registers :
			#print r.name
		        value = getRandomValue()
			values = [ value[0:8] , '0x'+value[8:16] ]
			r.addTestToCache( values[0]+" "+values[1] )
			#if not testRandomValue( r ) :
			#	result[q] = result[q] + 1
		#print "ERRORS: ",result

	for r in registers : 
		r.testCache()

# /MAIN

