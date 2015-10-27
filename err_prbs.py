####################################################################
# Type: SCRIPT                                                     #
#                                                                  #
# Description: This is a script skeleton.                          #
####################################################################

from hcal_teststand import *
from hcal_teststand.hcal_teststand import teststand
import sys
from time import sleep

# CLASSES:
# /CLASSES

# FUNCTIONS:

def main():
	name = "904"
	ts = teststand(name)		# This object stores the teststand configuration and has a number of useful methods.
	t = 5
	t = t - 2.1792182064
	k = 3
	errlist = {}
	errint = {}
	times = []
	sfp = int(raw_input("Pick the FC7 slot number to be tested (0 for all slots): "))
	d = bool(raw_input("Choose the error counter (0: FC7, 1: ngCCM): "))
	
	if d:
		if sfp:
			commands = ["get HF{0}-mezz_ERROR_COUNT".format(sfp)]
		else:
			commands = ["get HF{0}-mezz_ERROR_COUNT".format(i) for i in range(1, 7)]
	else:
		if sfp:
			commands = ["get fec1-sfp{0}_prbs_rx_pattern_error_cnt".format(sfp)]
		else:
			commands = ["get fec1-sfp{0}_prbs_rx_pattern_error_cnt".format(i) for i in range(1, 7)]
	for c in commands:
		errint.update({c: 0})
	outputi = ngfec.send_commands(ts=ts, cmds=commands)
#	print outputi
	times.append([sum(out["times"])/len(out["times"]) for out in outputi])
#	print times

	print "\nThe PRBS error counters(Now):"
#	counters = [int(i["result"], 16) for i in outputi]
	for result in outputi:
		print "\t{0} -> {1}".format(result["cmd"], int(result["result"], 16))

	for j in range(k):

		sleep(t)

		if d:
			if sfp:
				commands = ["get HF{0}-mezz_ERROR_COUNT".format(sfp)]
			else:
				commands = ["get HF{0}-mezz_ERROR_COUNT".format(i) for i in range(1, 7)]
		else:
			if sfp:
				commands = ["get fec1-sfp{0}_prbs_rx_pattern_error_cnt".format(sfp)]
			else:
				commands = ["get fec1-sfp{0}_prbs_rx_pattern_error_cnt".format(i) for i in range(1, 7)]
		outputf = ngfec.send_commands(ts=ts, cmds=commands)

		times.append([sum(out["times"])/len(out["times"]) for out in outputf])
		print "\nThe PRBS error counters(+{0:.3f}s):".format((sum(times[j+1])-sum(times[0]))/len(times[0]))
#		counters = [int(i["result"], 16) for i in outputf]
		for result in outputf:
			print "\t{0} -> {1}".format(result["cmd"], int(result["result"], 16))

		print "\nDifference:"
		for i in range(len(outputi)):
			de = int(outputf[i]["result"], 16) - int(outputi[i]["result"], 16)
			dt = sum(outputf[i]["times"])/len(outputf[i]["times"]) - sum(outputi[i]["times"])/len(outputi[i]["times"])
			print "\t{0} -> {1} | Error rate: {2:.4g} Hz".format(commands[i], de, de/float(dt))
#			if de:
#				errlist.update({"{0} - {1}s".format(j*t, (j+1)*t): [commands[i], de]})
#		outputi = outputf	Unnecessary?
	log = int(raw_input("Do you want to log the results? (1: Yes, 0: No): "))
	if log:
		sno = raw_input("Enter the S/N of the ngCCM: ")
		att = raw_input("Enter the attenuation value (dB): ")
		if d:
			f = open("prbs_log_ngccm_{0}.csv".format(sno), "a")
		elif de == 0 and "ERROR" in ngfec.send_commands(ts=ts, cmds=["get HF{0}-mezz_ERROR_COUNT".format(sfp)])[0]["result"]:
			de = -dt
			f = open("prbs_log_fc7_{0}.csv".format(sno), "a")
		else:
			f = open("prbs_log_fc7_{0}.csv".format(sno), "a")
		sys.stdout = f
		print sno + ", " + att + ", " + "{0}, {1}".format(de/float(dt), dt)
		sys.stdout = sys.__stdout__
	
#	print "\n=============SUMMARY============="
#	print "Errors:"
#	for key, value in errlist.iteritems():
#		print "\t{0} -> {1} between {2}".format(value[0], value[1], key)
#		errint[value[0]] += value[1]
#	print
#	print "Total errors:"
#	for c in commands[:-1]:
#	print "\t{0} -> {1}".format(c, errint[c])
#	print sno + ", " + att + "{0}, {1}".format(de/float(dt), dt)
#	print "=================================\n"
# /FUNCTIONS

# MAIN:

if __name__ == "__main__":
	main()
# /MAIN
