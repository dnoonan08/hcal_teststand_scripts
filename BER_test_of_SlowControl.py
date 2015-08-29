####################################################################
# Type: SCRIPT                                                     #
#                                                                  #
# Description: Perform n cycles where a cycle is the following:    #
# * Write 00...001 to the Bridge scratch register.                 #
# * Read back the value of the Bridge scratch register.            #
# * Check that they're the same. Report an error if they aren't    #
# * Repeat for 00...010 through 10...000 (32 read-writes total).   #
####################################################################

from hcal_teststand import *
from hcal_teststand.hcal_teststand import *
import sys
from optparse import OptionParser

# CLASSES:
# /CLASSES

# FUNCTIONS:
# /FUNCTIONS

# MAIN:
if __name__ == "__main__":
	# Arguments:
	crate = 1		# Crate number to run the test over
	slot = 2		# Slot number to run the test over
	parser = OptionParser()
	parser.add_option("-n", "--ncycles", dest="ncycles",
		default=1,
		help="The number of cycles you want to run over (default is 1)", metavar="INT")
	parser.add_option("-v", "--verbose", dest="verbose",
		action="store_true",
		default=False,
		help="Turn on verbose mode (default is off)",
		metavar="BOOL"
	)
	parser.add_option("-t", "--teststand", dest="ts",
		default="904",
		help="The name of the teststand you want to use (default is 904)", metavar="STR")
	(options, args) = parser.parse_args()
	name = options.ts
	n = int(options.ncycles)
	v = bool(options.verbose)
	if isinstance(options.verbose, str):
		if options.verbose.lower() == "true":
			v = True
		else:
			v = False
	
	# Set up:
	ts = teststand(name)		# Initialize a teststand object. This object stores the teststand configuration and has a number of useful methods.
	print ">> Running BER test on teststand {0}.".format(name)
	
	# Cycle n times:
	n_cycles = {}
	n_errors = {}
	n_errors_read = {}
	errors = {}
	for crate, slots in ts.fe.iteritems():
		for slot in slots:
			# Set up variables:
			n_cycles[crate, slot] = 0
			errors[crate, slot] = []
			n_errors[crate, slot] = 0
			n_errors_read[crate, slot] = 0
			
			# Start cycle
			print "\n>> Processing {0} cycle(s) for crate {1}, slot {2} ...".format(n, crate, slot)
			for j in range(n):
				# Do a cycle:
				if v: print "==== Cycle {0} ============================================".format(j + 1)
				script = []
				h_writes = []
				bs = []
				for i in range(1, 33):
					# Construct test string:
					b = "0" * (32 - i)
					b += "1"
					b += "0" * (i - 1)
					bs.append(b)
					
					# Convert test string to hex:
					h_write = "{0:#010x}".format(int(b, 2))
					
					# Construct script:
					script.append("put HF{0}-{1}-B_SCRATCH {2}".format(crate, slot, h_write))
					script.append("get HF{0}-{1}-B_SCRATCH".format(crate, slot))
					h_writes.append(h_write)
				
				# Perform writting and reading:
				print ">> Talking to ngccm server ..."
				output = ngfec.send_commands(ts=ts, cmds=script, script=False)
				
				# Deal with results:
				for i in range(1, 33):
					h_write = h_writes[i - 1]
					if v: print "Binary string to write: {0}".format(bs[i - 1])
					if v: print "Hex string to write: {0}".format(h_write)
					try:
						h_read = "{0:#010x}".format(int(output[i*2 - 1]["result"], 16))
					except:
						h_read = False
					for cmd in output[2*i-2:2*i]:
						if v: print "<< Command: {0} -> {1}".format(cmd["cmd"], cmd["result"])
					if v: print "Hex string read: {0}".format(h_read)
					
					# Check for error:
					if h_read and h_write != h_read:
						n_errors[crate, slot] += 1
						errors[crate, slot].append([h_write, h_read])
						if v: print "ERROR: The read value of {0} didn't match the written value of {1}.".format(h_read, h_write)
					elif not h_read:
						n_errors_read[crate, slot] += 1
						if v: print "ERROR: The written value of {0} could not be read back.".format(h_write)
					
					if v: print ""
				n_cycles[crate, slot] += 1
	
	# Summarize:
	print "===== SUMMARY ====="
	print "Results for the {0} teststand:".format(ts.name)
	for crate, slots in ts.fe.iteritems():
		for slot in slots:
			# Set up variables:
			s = "{0:2d}{1:2d}".format(crate, slot)
			
			# Print summary:
			print "\n= QIE card in crate {0}, slot {1}".format(crate, slot)
			print "Total number of cycles: {0}".format(n_cycles[crate, slot])
			print "! Number of mismatch errors: {0}".format(n_errors[crate, slot])
			if n_errors[crate, slot]:
				print "! Below is some information about these errors:"
				for i in range(len(errors[crate, slot])):
					print "{0}: string written = {1}, string read = {2}".format(i + 1, errors[crate, slot][i][0], errors[crate, slot][i][1])
			if n_errors_read[crate, slot] > 0 : print "! Number of software read errors: {0}".format(n_errors_read[crate, slot])
# /MAIN
