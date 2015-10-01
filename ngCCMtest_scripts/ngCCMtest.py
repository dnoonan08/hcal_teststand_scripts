####################################################################
# Type: SCRIPT                                                     #
#                                                                  #
# Description: ngCCM test script                                   #
####################################################################

import sys
sys.path.append('..')


from hcal_teststand import *
from hcal_teststand.hcal_teststand import teststand
import random
import os
from  ngCCMtest_functions import *
import optparse
from QIEtest_functions import *

class Logger(object):
	def __init__(self):
		self.terminal = sys.stdout
		self.log = open("ngCCM_904_log.txt","a")

	def write(self, message):
		self.terminal.write(message)
		self.log.write(message)

stdo_def = sys.stdout

# CLASSES:
# /CLASSES

# FUNCTIONS:
# /FUNCTIONS


start_dir = os.getcwd()
os.chdir('..')

name = '904'
ts = teststand(name)		# Initialize a teststand object. This object stores the teststand configuration and has a number of useful methods.

parser = optparse.OptionParser()
parser.add_option('-v','--verbose', help = 'Display full test output', dest = 'verbose', default = False, action = 'store_true')
parser.add_option('-l','--log', help = 'Log test results', dest = 'log', default = False, action = 'store_true')
(options, args) = parser.parse_args()

os.system("clear")

log = options.log
verbose = options.verbose

# Start working on the ngCCM:

if log == 1:
	SN = get_SN()
	sys.stdout = Logger()
	print "ngCCM SN: " + SN

os.chdir(start_dir)

m_r = 0
m_r = mezz_read(verbose,ts)

m_s = 0
m_s_num = 10
m_s = mezz_scratch(m_s_num,0,ts)

power_status = 0
power_status = check_power(ts)

# Start working on the QIE cards:

qie_s = 0
qie_r = 0
qie_num = 10
if power_status == 0:
	rst_results = ngccm.send_commands_parsed( ts, ["put HF2-bkp_reset 0", "put HF2-bkp_reset 1", "put HF2-bkp_reset 0"])  # Added by Tote.
        if verbose :
		print "Backplane reset issued as follows:"
		for c in rst_results["output"]:
			print c["cmd"] + " -> " + c["result"]
	qie_s = QIE(qie_num,0,ts)
	a,b,c,d = TestAll(ts,0,1,2)
	qie_r = a + b + c
	#qie = QIEs(qie_num,1,ts,[2])
else:
	print "***********************************************"
	print "Backplane power not enabled. Skipping QIE test."
	print "***********************************************"

# Continue work with the ngCCM:

adcs = 0
adcs = ADCs(verbose,ts)

sw = 0
sw = Check_SW(verbose,ts)


###################################
##   Prepare summary of results:

if m_r + m_s + qie_r + qie_s + adcs + sw == 0:
	print "*********************************"
	print "All tests completed successfully."
	print "*********************************"
else:
	print "***************************************"
	print "There were some errors during the test."
	print "***************************************"
	if m_r > 0:
		print "There were " + str(m_r) + " errors reading mezzanine registers."
	if m_s > 0:
		print "There were " + str(m_s) + " errors out of " + str(m_s_num) + " trials when writing/reading the mezzanine scratch register."

	if power_status == 1:
		print "There was a problem with the backplane power. The QIE test was skipped."
	if qie_s > 0:
		print "There were " + str(qie_s) + " errors out of " + str(qie_num) + " trials when writing/reading the QIE scratch register."
	if qie_r > 0:
		print "There were " + str(qie_r) + " errors when writing/reading the QIE registers."
	if adcs > 0:
		print "There were " + str(adcs) + " errors reading ngCCM ADCs."
        if sw > 0:
                print "There were " + str(sw) + " counting room switch signals that did not have the expected value."
	print "***************************************"
if log == 1:
	print ""
	sys.stdout = stdo_def
