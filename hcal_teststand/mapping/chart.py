####################################################################
# Type: MODULE                                                     #
#                                                                  #
# Description: [description]                                       #
####################################################################

# IMPORTS:
import os
#from optparse import OptionParser
#from ..hcal_teststand import teststand
#from ..utilities import time_string
from ..qie import qie
import json
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
			print "WARNING (mapping.chart.__init__): You should initialize a chart with the teststand name (like \"904at\")."
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
	
	def write(self, d="configuration/maps"):
		f = "{0}_qie_map.json".format(self.name)
		if not os.path.exists(d):
			os.makedirs(d)
		with open("{0}/{1}".format(d, f), "w") as out:
			json.dump(self.maps, out, indent=4, sort_keys=True)
	
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
	
	def get_qies(self, qid=None):		# "qid" argument isn't implemented...
		if self.maps:
			qies = []
			qids = list(set([chip["qie_id"] for chip in self.maps]))
			for q in qids:
				info = list(set([(chip["be_crate"], chip["be_slot"], chip["fe_crate"], chip["fe_slot"]) for chip in self.maps if chip["qie_id"] == q]))
				links = list(set([chip["uhtr_link"] for chip in self.maps if chip["qie_id"] == q]))
				if len(info) == 1 and len(links) == 6:
					qies.append(qie(
						be_crate=info[0][0],
						be_slot=info[0][1],
						crate=info[0][2],
						slot=info[0][3],
						links=links,
					))
				else:
					print "WARNING (chart.add_map): The QIE card information for {0} is confusing:\n\t{1}\n\t{2}".format(q, info, links)
			return qies
		else:
			print "ERROR (chart.get_qies): I don't know what information to use to get the qie objects because the chart's \"maps\" attribute is empty."
			return False
	# /Methods
# /CLASSES

# FUNCTIONS:
# /FUNCTIONS
