####################################################################
# Type: SCRIPT                                                     #
#                                                                  #
# Description: Reads in 100 BXs of SPY data from each active link  #
# and prints out the average and standard deviation.               #
####################################################################

from hcal_teststand import *
from hcal_teststand.hcal_teststand import *
import sys
import numpy

if __name__ == "__main__":
	name = ""
	if len(sys.argv) == 1:
		name = "904"
	elif len(sys.argv) == 2:
		name = sys.argv[1]
	else:
		name = "904"
	ts = teststand(name)

	ts.set_ped_all(6)
	qie.set_fix_range_all(ts, 1, 2, False)
	for uhtr_slot in ts.uhtr_slots:
		print "\nResults for the uHTR in slot {0}:".format(uhtr_slot)
		active_links = uhtr.find_links(ts, uhtr_slot)
		print "The activated links are {0}.".format(active_links)
		for link_i in active_links:
			print "==== Link {0} ====".format(link_i)
			uhtr_read = uhtr.get_data(ts, uhtr_slot, 300, link_i)
			data = uhtr.parse_data(uhtr_read["output"])
	#		print data["adc"]
			print "Read in {0} bunch crossings.".format(len(data["adc"]))
			for i in range(4):
				print "Channel {0}: ADC_avg = {1:.2f} (sigma = {2:.2f})".format(i, numpy.mean([i_bx[i] for i_bx in data["adc"]]), numpy.std([i_bx[i] for i_bx in data["adc"]]))
