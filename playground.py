from hcal_teststand import *
import uhtr
import ngccm
import numpy
import sys
import qie

if __name__ == "__main__":
	name = ""
	if len(sys.argv) == 1:
		name = "bhm"
	elif len(sys.argv) == 2:
		name = sys.argv[1]
	else:
		name = "bhm"
	ts = teststand(name)

