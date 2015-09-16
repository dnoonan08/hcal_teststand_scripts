from hcal_teststand import *
from hcal_teststand.register import *
from hcal_teststand.hcal_teststand import teststand
import sys
import random

# FUNCTIONS:
def getRandomValue( regSize=1 ) : 

	### 
	# the 47 should not be hardcoded and should instead
	# be taken from register.size.  However, this needs to 
	# be done carefully so taht the bits are divided up
	# into 24 bit chunks correctly...
	###
	randomInt = random.randint(0,2**regSize-1)	
	#regSize = regSize - 1    #biz ekledik
	#for i in range( regSize ) :
	#	if random.randint(0,1) : 
	#		randomInt = ( randomInt | 1 ) << 1    #bit aritmetigi << shift komutu 
	#	else :
	#		randomInt = randomInt << 1
	#if (randomInt =!0)
	#	randomInt = randomInt - random.randint(0,1)	#biz ekledik	
	return str(hex(randomInt))
		
def format_random_value(d):
        ab=[]
        a="0x"
        b="0x"
        c = getRandomValue(int(d))
        #c = d
        if (len(c) >= 18):
                for i in xrange(2,10):
                        a +=str(c[i])
                        #print ( int(a) % 32)
                for i in xrange(10,18):
                        b +=str(c[i])
                #print len(c), c
                
        else:
                r = 18 - len(c)
                if (r >= 9):
                        rr= 10 - len(c)
                        for i in xrange(8):
                                a +=str(0)
                        for i in xrange(rr):
                                b +=str(0)


                        for i in xrange((2),(10-rr)):
                                b +=str(c[i])
                        #print len(c), c

                else:
                        
                        for i in xrange(r):
                                a +=str(0)
                        for i in xrange(2,(10-r)):
                                a +=str(c[i])
                                
                        for i in xrange((10-r),(18-r)):
                                b +=str(c[i])
                        #print len(c), c
                        
        ab.append(a)
        ab.append(b)
        return ab       


def testRandomValue( register ):

	randomValue = getRandomValue( register.size )

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

	qieid="0xAA24DA70 0x8D000000"

	ts = teststand("904")		# Initialize a teststand object. This object stores the teststand configuration and has a number of useful methods.
	fe_crate, fe_slot = ts.crate_slot_from_qie(qie_id=qieid)
	#exit()
#	print ts.read_qie_map()
	registers = []
	for i_qie in range(1, 25):
        	registers.extend([
#			register(ts,"HF{0}-{1}-QIE{2}_Lvds".format(fe_crate, fe_slot, i_qie), 1),		# 1 bit
#			register(ts,"HF{0}-{1}-QIE{2}_Trim".format(fe_crate, fe_slot, i_qie),2),		# 2 bits trimden sonra 0x2
#			register(ts,"HF{0}-{1}-QIE{2}_DiscOn".format(fe_crate, fe_slot, i_qie),1),		# 1 bit discon sonra 0x0
#			register(ts,"HF{0}-{1}-QIE{2}_TGain".format(fe_crate, fe_slot, i_qie),1),		# 1 bit tgain den sonra 0x0
#			register(ts,"HF{0}-{1}-QIE{2}_TimingThresholdDAC".format(fe_crate, fe_slot, i_qie),8),		# 8 bits DAC sonra 0xff
#			register(ts,"HF{0}-{1}-QIE{2}_TimingIref".format(fe_crate, fe_slot, i_qie),3),		# 3 bits ref sonra 0x0
#			register(ts,"HF{0}-{1}-QIE{2}_PedestalDAC".format(fe_crate, fe_slot, i_qie),6),		# 6 bits dac sonra 0x26
#			register(ts,"HF{0}-{1}-QIE{2}_CapID0pedestal".format(fe_crate, fe_slot, i_qie),4),		# 4 bits tal sonra 0x0
#			register(ts,"HF{0}-{1}-QIE{2}_CapID1pedestal".format(fe_crate, fe_slot, i_qie),4),		# 4 bits tal sonra 0x0
#			register(ts,"HF{0}-{1}-QIE{2}_CapID2pedestal".format(fe_crate, fe_slot, i_qie),4),		# 4 bits  tal sonra 0x0
#			register(ts,"HF{0}-{1}-QIE{2}_CapID3pedestal".format(fe_crate, fe_slot, i_qie),4),		# 4 bits tal sonra 0x0
#			register(ts,"HF{0}-{1}-QIE{2}_FixRange".format(fe_crate, fe_slot, i_qie),1),		# 1 bit range sonra 0x0
#			register(ts,"HF{0}-{1}-QIE{2}_RangeSet".format(fe_crate, fe_slot, i_qie),2),		# 2 bits
#			register(ts,"HF{0}-{1}-QIE{2}_ChargeInjectDAC".format(fe_crate, fe_slot, i_qie),3),		# 3 bits
#			register(ts,"HF{0}-{1}-QIE{2}_RinSel".format(fe_crate, fe_slot, i_qie),4),		# 4 bits
#			register(ts,"HF{0}-{1}-QIE{2}_Idcset".format(fe_crate, fe_slot, i_qie),5),		# 5 bits
#			register(ts,"HF{0}-{1}-QIE{2}_CalMode".format(fe_crate, fe_slot, i_qie),1),		# 1 bit
#			register(ts,"HF{0}-{1}-QIE{2}_CkOutEn".format(fe_crate, fe_slot, i_qie),1),		# 1 bit
			register(ts,"HF{0}-{1}-QIE{2}_TDCMode".format(fe_crate, fe_slot, i_qie),1)		# ? bit
	               	#"HF{0}-{1}-QIE{2}_CalMode".format(fe_crate, fe_slot, i_qie),
	               	#"HF{0}-{1}-QIE{2}_ChargeInjectDAC".format(fe_crate, fe_slot, i_qie),
                	#"HF{0}-{1}-QIE{2}_Lvds".format(fe_crate, fe_slot, i_qie),
                	#"HF{0}-{1}-QIE{2}_TGain".format(fe_crate, fe_slot, i_qie),
                	#"HF{0}-{1}-QIE{2}_CapID0pedestal".format(fe_crate, fe_slot, i_qie),
                	#"HF{0}-{1}-QIE{2}_CkOutEn".format(fe_crate, fe_slot, i_qie),
                	#"HF{0}-{1}-QIE{2}_PedestalDAC".format(fe_crate, fe_slot, i_qie),
                	#"HF{0}-{1}-QIE{2}_TimingIref".format(fe_crate, fe_slot, i_qie),
                	#"HF{0}-{1}-QIE{2}_CapID1pedestal".format(fe_crate, fe_slot, i_qie),
           		#"HF{0}-{1}-QIE{2}_DiscOn".format(fe_crate, fe_slot, i_qie),
                	#"HF{0}-{1}-QIE{2}_RangeSet".format(fe_crate, fe_slot, i_qie),
                	#"HF{0}-{1}-QIE{2}_TimingThresholdDAC".format(fe_crate, fe_slot, i_qie),
                	#"HF{0}-{1}-QIE{2}_CapID2pedestal".format(fe_crate, fe_slot, i_qie),
                	#"HF{0}-{1}-QIE{2}_FixRange".format(fe_crate, fe_slot, i_qie),
                	#"HF{0}-{1}-QIE{2}_RinSel".format(fe_crate, fe_slot, i_qie),
                	#"HF{0}-{1}-QIE{2}_Trim".format(fe_crate, fe_slot, i_qie),
                	#"HF{0}-{1}-QIE{2}_CapID3pedestal".format(fe_crate, fe_slot, i_qie),
                	#"HF{0}-{1}-QIE{2}_Idcset".format(fe_crate, fe_slot, i_qie),
                	#"HF{0}-{1}-QIE{2}_TDCMode".format(fe_crate, fe_slot, i_qie),
        	])

	result = [0]*24
#	registers = []
#	for name in register_names:
#		registers.append(register(ts, name, 1))		# HERE on "48"

	for i in range( 5 ) :
		#print "test",i
		for r in registers :
			#print r.name
		        value = getRandomValue( r.size )
			values = [ value[0:8]] #, '0x'+value[8:16] ]
			r.addTestToCache( values[0]) #+" "+values[1] )
			#if not testRandomValue( r ) :
			#	result[q] = result[q] + 1
		#print "ERRORS: ",result

	for r in registers : 
		r.testCache()

# /MAIN

