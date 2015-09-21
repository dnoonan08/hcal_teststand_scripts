####################################################################
# Type: MODULE                                                     #
#                                                                  #
# Description: [description]                                       #
####################################################################

# IMPORTS:
#import os
#from optparse import OptionParser
#from ..hcal_teststand import teststand
#from ..utilities import time_string
#import ROOT
# /IMPORTS

# VARIABLES:
#ts = teststand("904at")
# /VARIABLES

# CLASSES:
class chart:
	# Construction:
	def __init__(self, name=None, maps=[]):
		# Assign argument variables:
		if name:
			self.name = name
		else:
			print "WARNING (mapping.chart.__init__): You should initialize a chart with the teststand name (like \"904\")."
		if not maps:
			self.maps = []
	# /Construction
	
	# Methods:
	def Print(self, v=True):
		if self.maps:
			pretty = "[\n"
			for m in self.maps:
				pretty += "\t{0},\n".format(m)
			pretty += "]"
			if v: print pretty
			return pretty
		else:
			if v: print "[]"
			return False
	
	def add_map(self, qie_map=None):
		if isinstance(qie_map, list):
			self.maps.extend(qie_map)
			return True
		elif isinstance(qie_map, dict):
			self.maps.append(qie_map)
			return True
		else:
			print "ERROR (chart.add_map): You tried to add something that didn't look like a map (or maps)."
			return False
	# /Methods
# /CLASSES

# FUNCTIONS:
# /FUNCTIONS
