####################################################################
# Type: MODULE                                                     #
#                                                                  #
# Description: [description]                                       #
####################################################################

# IMPORTS:
import os
from optparse import OptionParser
from ..hcal_teststand import teststand
from ..utilities import time_string
import ROOT
# /IMPORTS

# VARIABLES:
#ts = teststand("904at")
# /VARIABLES

# CLASSES:
class acceptance:
	# Construction:
	def __init__(self, name=None):
		# Assign argument variables:
		if name:
			self.name = name
			if (self.name.split("_")[0] == "at"):		# Remove a preceding "at_" if there is one.
				self.name = self.name[3:]
		else:
			print "WARNING (tests.acceptance.__init__): You need to initialize an acceptance test with the three character name (like \"reg\")."
		
		# Assign commandline option variables:
		## Define commandline options:
		### Teststand:
		parser = OptionParser()
		parser.add_option("-t", "--teststand", dest="ts",
			default="904at",
			help="The name of the teststand you want to use (default is \"904\")",
			metavar="STR"
		)
		### QIE ID:
		parser.add_option("-q", "--qid", dest="qid",
			default="0x67000000 0x9B32C370",
			help="The unique ID of the QIE card you're testing",
			metavar="STR"
		)
		parser.add_option("-v", "--verbose", dest="v",
			action="store_true",
			default=False,
			help="Turn on verbose mode (default is off)",
			metavar="BOOL"
		)
#		parser.add_option("-o", "--fileName", dest="out",
#			default="",
#			help="The name of the directory you want to output plots to (default is \"data/at_results/[QIE_CARD_ID]\").",
#			metavar="STR"
#		)
#		parser.add_option("-n", "--nReads", dest="n",
#			default=10,
#			help="The number of groups of 100 BXs you want to read per link per phase setting (defualt is 10).",
#			metavar="INT"
#		)
		(options, args) = parser.parse_args()
		
		## Assign variables:
		self.ts_name = options.ts
		self.qid = options.qid
		self.verbose = self.v = options.v
		
		# Other variables:
		self.ts = teststand(self.ts_name)
		self.time_string = time_string()[:-4]
		self.path = "data/at_results/{0}/at_{1}/{2}".format(self.qid.replace(" ", "_"), self.name, self.time_string)
		if not os.path.exists(self.path):
			os.makedirs(self.path)
		self.file_name = "{0}_{1}".format(self.time_string, self.name)
		self.out = ROOT.TFile("{0}/{1}.root".format(self.path, self.file_name), "RECREATE")
		ROOT.SetOwnership(self.out, 0)
		self.tc = ROOT.TCanvas("c0", "c0", 500, 500)
		self.tc.SetFillColor(ROOT.kWhite)
		ROOT.SetOwnership(self.tc, 0)
		
		# ROOT settings:
		ROOT.gROOT.SetStyle("Plain")
		ROOT.gROOT.SetBatch()
	# /Construction
	
	# Methods:
	def write(self):
		self.tc.SaveAs("{0}/{1}.png".format(self.path, self.file_name))
		self.tc.SaveAs("{0}/{1}.pdf".format(self.path, self.file_name))
		self.out.Close()
	# /Methods
# /CLASSES

# FUNCTIONS:
# /FUNCTIONS
