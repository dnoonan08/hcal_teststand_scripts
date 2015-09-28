from hcal_teststand import *
from hcal_teststand.register import *
from hcal_teststand.hcal_teststand import teststand
import sys
import random
from ROOT import *


# FUNCTIONS:
def getRandomValue( regSize=1 ) : 

	### 
	# the 47 should not be hardcoded and should instead
	# be taken from register.size.  However, this needs to 
	# be done carefully so taht the bits are divided up
	# into 24 bit chunks correctly...
	###

	output = ""

	if regSize % 32:
		output += str(hex(random.randint(0, 2**(regSize % 32-1))) + " ")

	for i in range(int(regSize/32)):
		output += str(hex(random.randint(0, 2**32-1))) + " "
	output = output[:-1]

	return output

#	randomInt = str(hex(random.randint(0,2**regSize-1)))
#	return randomInt
	
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


def create_plots(names = None, dic = None, n = 1):
	tf = TFile("AT_REG.root", "RECREATE")
	gROOT.SetStyle("Plain")
	gStyle.SetOptStat(0)
	c1 = TCanvas("c1", "Register Test", 500, 500)
	c1.Divide(1, n)
#	c1.SetTitle("")
	totals = []
	errs = []
	execs = []
	stacks = []
	for i in range(n):
		namespart = names[i*len(names)/n:(i+1)*len(names)/n]	# On (i+1)*len(names)/n, first i*len(names) is done, then the division by n. By that way, i = n - 1 => (i+1)*len(names)/n = len(names). So we don't lose any bins because of integer division.
		totals.append(TH1F("Total_{0}".format(i+1), "", len(namespart), -0.5, len(namespart)-0.5))
		errs.append(TH1F("Err_{0}".format(i+1), "", len(namespart), -0.5, len(namespart)-0.5))
		execs.append(TH1F("Exec_{0}".format(i+1), "", len(namespart), -0.5, len(namespart)-0.5))
		stacks.append(THStack("Error_{0}".format(i+1), ""))
		totals[i].SetFillColor(kGreen)
		errs[i].SetFillColor(kRed)
		execs[i].SetFillColor(kOrange)
		for j, name in enumerate(namespart):
			totals[i].GetXaxis().SetBinLabel(j+1, name) 
			errs[i].GetXaxis().SetBinLabel(j+1, name)
			execs[i].GetXaxis().SetBinLabel(j+1, name)
			totals[i].Fill(j, dic[name][0])
			errs[i].Fill(j, dic[name][1])
			execs[i].Fill(j, dic[name][2])
		totals[i].GetXaxis().LabelsOption("vd")
		errs[i].GetXaxis().LabelsOption("vd")
		execs[i].GetXaxis().LabelsOption("vd")
#		errs[i].Fill(random.randint(0, len(namespart)-1))
#		execs[i].Fill(random.randint(0, len(namespart)-1))
#		errs[i].Fill(0)
#		execs[i].Fill(2)
#		errs[i].Fill(len(namespart)-4)
#		errs[i].Fill(len(namespart)-3)
#		execs[i].Fill(len(namespart)-1)
		c1.cd(i+1)
		c1.SetTitle("")
#		gPad.SetBottomMargin(-10)
		gPad.SetLogy(1)
		totals[i].Write()
		errs[i].Write()
		execs[i].Write()
		stacks[i].Add(errs[i])
		stacks[i].Add(execs[i])
		stacks[i].Write()
		totals[i].Draw()
		stacks[i].Draw("SAME")
	c1.Write()
	c1.SaveAs("AT_REG.pdf")
#	return 0

# /FUNCTIONS

# MAIN:
if __name__ == "__main__":

	qieid="0x67000000 0x9B32C370"
#	qieid="0xAA24DA70 0x8D000000"

	ts = teststand("904")		# Initialize a teststand object. This object stores the teststand configuration and has a number of useful methods.
	fe_crate, fe_slot = ts.crate_slot_from_qie(qie_id=qieid)
	#exit()
#	print ts.read_qie_map()
	registers = []
	for i_qie in range(1, 25):
		registers.extend([
			register(ts, "HF{0}-{1}-QIE{2}_Lvds".format(fe_crate, fe_slot, i_qie), 1),		# 1 bit
			register(ts, "HF{0}-{1}-QIE{2}_Trim".format(fe_crate, fe_slot, i_qie), 2),		# 2 bits
			register(ts, "HF{0}-{1}-QIE{2}_DiscOn".format(fe_crate, fe_slot, i_qie), 1),		# 1 bit
			register(ts, "HF{0}-{1}-QIE{2}_TGain".format(fe_crate, fe_slot, i_qie), 1),		# 1 bit
			register(ts, "HF{0}-{1}-QIE{2}_TimingThresholdDAC".format(fe_crate, fe_slot, i_qie), 8),		# 8 bits
			register(ts, "HF{0}-{1}-QIE{2}_TimingIref".format(fe_crate, fe_slot, i_qie), 3),	# 3 bits
			register(ts, "HF{0}-{1}-QIE{2}_PedestalDAC".format(fe_crate, fe_slot, i_qie), 6),	# 6 bits
			register(ts, "HF{0}-{1}-QIE{2}_CapID0pedestal".format(fe_crate, fe_slot, i_qie), 4),	# 4 bits
			register(ts, "HF{0}-{1}-QIE{2}_CapID1pedestal".format(fe_crate, fe_slot, i_qie), 4),	# 4 bits
			register(ts, "HF{0}-{1}-QIE{2}_CapID2pedestal".format(fe_crate, fe_slot, i_qie), 4),	# 4 bits
			register(ts, "HF{0}-{1}-QIE{2}_CapID3pedestal".format(fe_crate, fe_slot, i_qie), 4),	# 4 bits
			register(ts, "HF{0}-{1}-QIE{2}_FixRange".format(fe_crate, fe_slot, i_qie), 1),		# 1 bit
			register(ts, "HF{0}-{1}-QIE{2}_RangeSet".format(fe_crate, fe_slot, i_qie), 2),		# 2 bits
			register(ts, "HF{0}-{1}-QIE{2}_ChargeInjectDAC".format(fe_crate, fe_slot, i_qie), 3),	# 3 bits
			register(ts, "HF{0}-{1}-QIE{2}_RinSel".format(fe_crate, fe_slot, i_qie), 4),		# 4 bits
			register(ts, "HF{0}-{1}-QIE{2}_Idcset".format(fe_crate, fe_slot, i_qie), 5),		# 5 bits
			register(ts, "HF{0}-{1}-QIE{2}_CalMode".format(fe_crate, fe_slot, i_qie), 1),		# 1 bit
			register(ts, "HF{0}-{1}-QIE{2}_CkOutEn".format(fe_crate, fe_slot, i_qie), 1),		# 1 bit
			register(ts, "HF{0}-{1}-QIE{2}_TDCMode".format(fe_crate, fe_slot, i_qie), 1),		# 1 bit
			register(ts, "HF{0}-{1}-Qie{2}_ck_ph".format(fe_crate, fe_slot, i_qie), 4),		# 4 bits
		])
		
	registers.extend([
		register(ts, "HF{0}-{1}-iBot_CntrReg_CImode".format(fe_crate, fe_slot), 1),		# 1 bit
		register(ts, "HF{0}-{1}-iBot_CntrReg_InternalQIER".format(fe_crate, fe_slot), 1),	# 1 bit
		register(ts, "HF{0}-{1}-iBot_CntrReg_OrbHistoClear".format(fe_crate, fe_slot), 1),	# 1 bit
		register(ts, "HF{0}-{1}-iBot_CntrReg_OrbHistoRun".format(fe_crate, fe_slot), 1),	# 1 bit
		register(ts, "HF{0}-{1}-iBot_CntrReg_WrEn_InputSpy".format(fe_crate, fe_slot), 1),	# 1 bit
		register(ts, "HF{0}-{1}-iBot_AddrToSERDES".format(fe_crate, fe_slot), 16),		# 16 bits
		register(ts, "HF{0}-{1}-iBot_CtrlToSERDES_i2c_go".format(fe_crate, fe_slot), 1),	# 1 bit
		register(ts, "HF{0}-{1}-iBot_CtrlToSERDES_i2c_write".format(fe_crate, fe_slot), 1),	# 1 bit
		register(ts, "HF{0}-{1}-iBot_DataToSERDES".format(fe_crate, fe_slot), 32),		# 32 bits
		register(ts, "HF{0}-{1}-iBot_LinkTestMode".format(fe_crate, fe_slot), 8),		# 8 bits
		register(ts, "HF{0}-{1}-iBot_LinkTestPattern".format(fe_crate, fe_slot), 32),		# 32 bits
#		register(ts, "HF{0}-{1}-iBot_fifo_data_1".format(fe_crate, fe_slot), ?),	# Seems r/o
#		register(ts, "HF{0}-{1}-iBot_fifo_data_2".format(fe_crate, fe_slot), ?),	# Seems r/o
#		register(ts, "HF{0}-{1}-iBot_fifo_data_3".format(fe_crate, fe_slot), ?),	# Seems r/o
		register(ts, "HF{0}-{1}-iBot_scratch".format(fe_crate, fe_slot), 32),			# 32 bits
		register(ts, "HF{0}-{1}-iBot_UniqueID".format(fe_crate, fe_slot), 64),			# 64 bits

		register(ts, "HF{0}-{1}-iTop_CntrReg_CImode".format(fe_crate, fe_slot), 1),		# 1 bit
		register(ts, "HF{0}-{1}-iTop_CntrReg_InternalQIER".format(fe_crate, fe_slot), 1),	# 1 bit
		register(ts, "HF{0}-{1}-iTop_CntrReg_OrbHistoClear".format(fe_crate, fe_slot), 1),	# 1 bit
		register(ts, "HF{0}-{1}-iTop_CntrReg_OrbHistoRun".format(fe_crate, fe_slot), 1),	# 1 bit
		register(ts, "HF{0}-{1}-iTop_CntrReg_WrEn_InputSpy".format(fe_crate, fe_slot), 1),	# 1 bit
		register(ts, "HF{0}-{1}-iTop_AddrToSERDES".format(fe_crate, fe_slot), 16),		# 16 bits
		register(ts, "HF{0}-{1}-iTop_CtrlToSERDES_i2c_go".format(fe_crate, fe_slot), 1),	# 1 bit
		register(ts, "HF{0}-{1}-iTop_CtrlToSERDES_i2c_write".format(fe_crate, fe_slot), 1),	# 1 bit
		register(ts, "HF{0}-{1}-iTop_DataToSERDES".format(fe_crate, fe_slot), 32),		# 32 bits
		register(ts, "HF{0}-{1}-iTop_LinkTestMode".format(fe_crate, fe_slot), 8),		# 8 bit
		register(ts, "HF{0}-{1}-iTop_LinkTestPattern".format(fe_crate, fe_slot), 32),		# 32 bits
#		register(ts, "HF{0}-{1}-iTop_fifo_data_1".format(fe_crate, fe_slot), ?),	# Seems r/o
#		register(ts, "HF{0}-{1}-iTop_fifo_data_2".format(fe_crate, fe_slot), ?),	# Seems r/o
#		register(ts, "HF{0}-{1}-iTop_fifo_data_3".format(fe_crate, fe_slot), ?),	# Seems r/o
		register(ts, "HF{0}-{1}-iTop_scratch".format(fe_crate, fe_slot), 32),			# 32 bits
		register(ts, "HF{0}-{1}-iTop_UniqueID".format(fe_crate, fe_slot), 30)			# 64 bits
        ])

#	result = [0]*24
#	registers = []
#	for name in register_names:
#		registers.append(register(ts, name, 1))		# HERE on "48"

	names = []
	for r in registers:
		names.append(r.name)

	for i in range( 5 ) :
		#print "test",i
		for r in registers :
#			print r.name
#			value = getRandomValue( r.size )
#			values = [value[0:32]] #, '0x'+value[8:16] ]
			r.addTestToCache( getRandomValue( r.size ) ) #+" "+values[1]
			#if not testRandomValue( r ) :
			#	result[q] = result[q] + 1
		#print "ERRORS: ",result
	tex = {}
	errd = {}
	for r in registers :
		r.setVerbosity(1)   # 0: not verbose, 1: verbose, 2: extra verbose
		r.testCache()
		errd.update({r.name: r.elist})
#		print r.tex[r.name]
		tex.update(r.tex)
#	print tex


#---------------Last report of errors------------------
	print "SUMMARY:"	
	for r in registers:
		if errd[r.name] != []:
			print "Error: " + r.name,
			for i in range(len(errd[r.name])):
				print str(tuple(errd[r.name][i])) + ",",
			print "\b\b",
			print ""
	print
#---------------Create histogram-----------------------
	create_plots(names, tex, 8)

# /MAIN
