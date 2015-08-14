####################################################################
# Type: MODULE                                                     #
#                                                                  #
# Description: This module contains functions for talking to the   #
# ngCCM and the ngccm tool (terribly named).                       #
####################################################################

from re import search, escape
from subprocess import Popen, PIPE
import pexpect
from time import time, sleep
from print_table import *


# CLASSES:
class status:
	# Construction:
	def __init__(self, ts=None, status=[], crate=-1, fw=[]):
		if not ts:
			ts = None
		self.ts = ts
		if not status:
			status = []
		self.status = status
		self.crate = crate
		if not fw:
			fw = []
		self.fw = fw
		if len(self.fw) == 2:
			self.fw_major = self.fw[0]
			self.fw_minor = self.fw[1]
		else:
			self.fw_major = -1
			self.fw_minor = -1
	
	# String behavior
	def __str__(self):
		if self.ts:
			return "<ngccm.status object: {0}>".format(self.status)
		else:
			return "<empty ngccm.status object>"
	
	# Methods:
	def update(self):
		self.good = (False, True)[bool(self.status) and len(self.status) == sum(self.status)]
		if len(self.fw) == 2:
			self.fw_major = self.fw[0]
			self.fw_minor = self.fw[1]
	
	def Print(self, verbose=True):
		if verbose:
			print "[{0}] ngCCM of crate {1} status: {2} <- {3}".format(("!!", "OK")[self.good], self.crate, ("BAD", "GOOD")[self.good], self.status)
			if self.good:
				print "\tFW major: {0}".format(self.fw_major)
				print "\tFW minor: {0}".format(self.fw_minor)
		else:
			print "[{0}] ngCCM of crate {1} status: {2}".format(("!!", "OK")[self.good], self.crate, ("BAD", "GOOD")[self.good])
	
	def log(self):
		output = "%% ngCCM {0}\n".format(self.crate)
		output += "{0}\n".format(int(self.good))
		output += "{0}\n".format(self.status)
		output += "{0}\n".format(self.fw)
		return output.strip()
	# /methods
# /CLASSES

# FUNCTIONS:
def send_commands(ts, cmds):		# Executes ngccm commands in the slowest way, in order to read all of the output.
	log = ""
	raw_output = ""
	if isinstance(cmds, str):
		cmds = [cmds]
	if "quit" not in cmds:
		cmds.append("quit")
	ngfec_cmd = 'ngFEC.exe -z -c -p {0}'.format(ts.ngccm_port)
	if hasattr(ts, "control_hub"):
		ngfec_cmd += " -H {0}".format(ts.control_hub)
	p = pexpect.spawn(ngfec_cmd)
	log += "----------------------------\nYou ran the following script with the ngccm tool:\n"
	for c in cmds:
#		print ">> {0}".format(c)
		p.sendline(c)
		if c != "quit":
			p.expect("{0} #\s|E.*\n".format(c))		# Sometimes a line will come in looking like "get fec1-ctrl #completions = 65844", which should not be grabbed. (So when there's no whitespace it needs to be E for error.)
			raw_output += p.before + p.after
		log += c + "\n"
	log += "----------------------------\n"
	p.expect(pexpect.EOF)
	raw_output += p.before
	return {
		"output": raw_output.strip(),
		"log": log.strip(),
	}

def send_commands_parsed(ts, cmds):		# This executes commands as above, but returns the parsed responses in a list of pairs.
	log = ""
	output = []
	if isinstance(cmds, str):
		cmds = [cmds]
	if "quit" not in cmds:
		cmds.append("quit")
	try:
		ngfec_cmd = 'ngFEC.exe -z -c -p {0}'.format(ts.ngccm_port)
		if hasattr(ts, "control_hub"):
			ngfec_cmd += " -H {0}".format(ts.control_hub)
		p = pexpect.spawn(ngfec_cmd)
		log += "----------------------------\nYou ran the following script with the ngccm tool:\n"
		for c in cmds:
			p.sendline(c)
			t0 = time()
			if c != "quit":
				p.expect("{0} #((\s|E).*)\n".format(escape(c)))
				t1 = time()
				output.append({
					"cmd": c,
					"result": p.match.group(1).strip().replace("'", ""),
					"times": [t0, t1],
				})
	#			print output
			else:
				sleep(1)
			log += c + "\n"
		p.close()
	except Exception as ex:
		print ex
		log += str(ex)
	log += "----------------------------\n"
	return {
		"output": output,
		"log": log.strip(),
	}

def send_commands_fast(ts, cmds):		# This executes ngccm commands in a fast way, but some "get" results might not appear in the output.
	log = ""
	raw_output = ""
	if isinstance(cmds, str):
		cmds = [cmds]
	cmds_str = ""
	for c in cmds:
		cmds_str += "{0}\n".format(c)
	cmds_str += "quit\n"
	log += "----------------------------\nYou ran the following script with the uHTRTool:\n\n{0}\n----------------------------".format(cmds_str)
	ngfec_cmd = 'ngFEC.exe -z -c -p {0}'.format(ts.ngccm_port)
	if hasattr(ts, "control_hub"):
		ngfec_cmd += " -H {0}".format(ts.control_hub)
	p = Popen(['printf "{0}" | {1}'.format(cmds_str, ngfec_cmd)], shell = True, stdout = PIPE, stderr = PIPE)
	raw_output_temp = p.communicate()		# This puts the output of the commands into a list called "raw_output_temp" the first element of the list is stdout, the second is stderr.
	raw_output += raw_output_temp[0] + raw_output_temp[1]
	return {
		"output": raw_output,
		"log": log.strip(),
	}

def get_info(ts, crate):		# Returns a dictionary of information about the ngCCM, such as the FW versions.
	log =""
	version_fw_mez_major = -1
	version_fw_mez_minor = -1
#	command = "get HF{0}-mezz_reg4".format(crate)		# Deprecated
	cmds = [
		"get HF{0}-mezz_FPGA_MAJOR_VERSION".format(crate),
		"get HF{0}-mezz_FPGA_MINOR_VERSION".format(crate),
	]
	output = send_commands_parsed(ts, cmds)["output"]
	result = output[0]["result"]
	if "ERROR" not in output[0]["result"]:
#		version_str_x = "{0:#08x}".format(int(match.group(3),16))		# Deprecated
#		version_fw_mez_major = int(version_str_x[-2:], 16)		# Deprecated
#		version_fw_mez_minor = int(version_str_x[-4:-2], 16)		# Deprecated
		version_fw_mez_major = int(output[0]["result"])
	if "ERROR" not in output[1]["result"]:
		version_fw_mez_minor = int(output[1]["result"])
#	else:
#		log += ">> ERROR: Failed to find FW versions. The command result follows:\n{0} -> {1}".format(cmd, result)
	version_fw_mez = "{0:02d}.{1:02d}".format(version_fw_mez_major, version_fw_mez_minor)
	return {
		"version_fw_mez_major":	version_fw_mez_major,
		"version_fw_mez_minor":	version_fw_mez_minor,
		"version_fw_mez":	version_fw_mez,
		"version_sw":	"?",
		"log":			log.strip(),
	}

#def setup(ts):
#	log = []
#	output = []
#	
#	if ts:
#		for crate in ts.fe_crates:
#			result = True
#			cmds = [
#				"put HF{0}-bkp_pwr_enable 0".format(crate),
#				"put HF{0}-bkp_pwr_enable 1".format(crate),
#				"put HF{0}-bkp_reset 1".format(crate),
#				"put HF{0}-bkp_reset 0".format(crate),
#				"get HF{0}-bkp_pwr_bad".format(crate),
#			]
#			results = send_commands_parsed(ts, cmds)["output"]
#			for cmd in results:
#				log.append(cmd)
#			for cmd in results[:-1]:
#				if "OK" not in cmd["result"]:
#					result = False
#			if results[-1]["result"] == "1":
#				result = False
#			output.append(result)
#		return {
#			"result": output,		# A list of booleans, one for each crate.
#			"log": log,		# A list of all ngccm commands sent.
#		}
#	else:
#		return {
#			"result": output,
#			"log": log,
#		}

def get_status(ts=None, crate=-1):		# Perform basic checks of the ngCCMs:
	log = ""
	s = status(ts=ts, crate=crate)
	
	if ts:
		# Check that versions are accessible:
		if crate in ts.fe_crates:
			s.crate = crate
			ngccm_info = get_info(ts, crate)
			s.fw = [
				ngccm_info["version_fw_mez_major"],
				ngccm_info["version_fw_mez_minor"]
			]
			if (s.fw[0] != -1):
				s.status.append(1)
			else:
				s.status.append(0)
			s.update()
		else:
			print "ERROR (ngccm.get_status): The crate you want ({0}) is not in the teststand object you supplied.".format(crate)
		
#		# Check the temperature:
#		temp = ts.get_temps()[0]
#		status["temp"] = temp
#		if ts.name == "bhm":
#			if (temp != -1) and (temp < 30.5):
#				status["status"].append(1)
#			else:
#				status["status"].append(0)
#		else:
#			if (temp != -1) and (temp < 37):
#				status["status"].append(1)
#			else:
#				status["status"].append(0)
	return s

def get_status_all(ts=None):
	log = ""
	ss = []
	
	if ts:
		for crate in ts.fe_crates:
			ss.append(get_status(ts=ts, crate=crate))
	return ss

def get_status_bkp(ts):		# Perform basic checks of the FE crate backplanes:
	log = ""
	status = {}
	status["status"] = []
	# Enable, reset, and check the BKP power:
	for crate in ts.fe_crates:
		ngccm_output = send_commands_fast(ts, ["put HF{0}-bkp_pwr_enable 1".format(crate), "put HF{0}-bkp_reset 1".format(crate), "put HF{0}-bkp_reset 0".format(crate)])["output"]
		log += ngccm_output
		ngccm_output = send_commands_fast(ts, "get HF{0}-bkp_pwr_bad".format(crate))["output"]
		log += ngccm_output
		match = search("{0} # ([01])".format("get HF{0}-bkp_pwr_bad".format(crate)), ngccm_output)
		if match:
			status["status"].append((int(match.group(1))+1)%2)
		else:
			log += "ERROR: Could not find the result of \"{0}\" in the output.".format("get HF{0}-bkp_pwr_bad".format(crate))
			status["status"].append(0)
	return status

def get_power(ts=False):
	output = {}
	
	if ts:
		for crate in ts.fe_crates:
			cmds = [
				"get HF{0}-VIN_voltage_f".format(crate),
				"get HF{0}-VIN_current_f".format(crate),
				"get HF{0}-3V3_voltage_f".format(crate),
				"get HF{0}-3V3_current_f".format(crate),
				"get HF{0}-2V5_voltage_f".format(crate),
				"get HF{0}-2V5_current_f".format(crate),
				"get HF{0}-1V5_voltage_f".format(crate),
				"get HF{0}-1V5_current_f".format(crate),		# This is really the current of 1.5 V plust the current of 1.2 V.
				"get HF{0}-1V2_voltage_f".format(crate),
			]
			output[crate] = send_commands_parsed(ts, cmds)["output"]
			return output
	else:
		return output

# enable CI mode
def set_CI_mode(ts , crate , slot , enable = True , DAC = 0 ) :
	
	if( enable ) :
		commands = [#" put HF{0}-{1}-iTop_CntrReg_CImode 1".format(crate,slot)]
			    #"put HF{0}-{1}-iBot_CntrReg_CImode 1".format(crate,slot)
			    "put HF{0}-{1}-QIE1_ChargeInjectDAC {0}".format(crate,slot,DAC)]
	else : 		
		commands = [" put HF{0}-{1}-iTop_CntrReg_CImode 0".format(crate,slot)]
			    #"put HF{0}-{1}-iBot_CntrReg_CImode 0".format(crate,slot)]

	
	ngccm_output = send_commands_parsed( ts , commands )

# This function should be moved to "qie.py":
def get_qie_shift_reg(ts , crate , slot , qie_list = range(1,5) ):
	
	qie_settings = [ "CalMode", 
			 "CapID0pedestal", 
			 "CapID1pedestal", 
			 "CapID2pedestal", 
			 "CapID3pedestal", 
			 "ChargeInjectDAC", 
			 "DiscOn", 
			 "FixRange", 
			 "IdcBias", 
			 "IsetpBias", 
			 "Lvds", 
			 "PedestalDAC",
			 "RangeSet", 
			 "TGain", 
			 "TimingIref", 
			 "TimingThresholdDAC",
			 "Trim"]
	
	table = [qie_settings]
	qieLabels = ["setting"]
	commands = []
	for qie in qie_list :
		#print qie
		for setting in qie_settings : 
			commands.append("get HF{0}-{1}-QIE{2}_{3}".format(crate,slot,qie,setting))
	
	ngccm_output = send_commands_parsed(ts , commands)
	
	for qie in qie_list : 
		qieLabels.append("QIE {0}".format(qie))
		values = []
		for i in ngccm_output["output"] : 		
			for setting in qie_settings : 
				if setting in i["cmd"] and "QIE{0}".format(qie) in i["cmd"]:
					values.append( i["result"] )
				
		table.append( values ) 
	
	#print table
	table_ = [ qieLabels ] 
	for i in zip(*table) : 
		table_.append(i)
	
	print_table(table_)
# /FUNCTIONS

# VARIABLES:
cmds_HF1_2 = [
	"get HF1-2-B_Adc",
	"get HF1-2-QIE16_FixRange",
	"get HF1-2-QIE2_CapID0pedestal",
	"get HF1-2-iBot_AddrToSERDES",
	"get HF1-2-B_BkPln_GEO",
	"get HF1-2-QIE16_IdcBias",
	"get HF1-2-QIE2_CapID1pedestal",
	"get HF1-2-iBot_CapIdErrLink1_count",
	"get HF1-2-B_BkPln_RES_QIE",
	"get HF1-2-QIE16_IsetpBias",
	"get HF1-2-QIE2_CapID2pedestal",
	"get HF1-2-iBot_CapIdErrLink2_count",
	"get HF1-2-B_BkPln_Spare_1_Counter",
	"get HF1-2-QIE16_Lvds",
	"get HF1-2-QIE2_CapID3pedestal",
	"get HF1-2-iBot_CapIdErrLink3_count",
	"get HF1-2-B_BkPln_Spare_2_Counter",
	"get HF1-2-QIE16_PedestalDAC",
	"get HF1-2-QIE2_ChargeInjectDAC",
	"get HF1-2-iBot_Clk_count",
	"get HF1-2-B_BkPln_Spare_3_Counter",
	"get HF1-2-QIE16_RangeSet",
	"get HF1-2-QIE2_DiscOn",
	"get HF1-2-iBot_CntrReg_CImode",
	"get HF1-2-B_BkPln_WTE",
	"get HF1-2-QIE16_TGain",
	"get HF1-2-QIE2_FixRange",
	"get HF1-2-iBot_CtrlToSERDES_i2c_go",
	"get HF1-2-B_Bottom_RESET_N",
	"get HF1-2-QIE16_TimingIref",
	"get HF1-2-QIE2_IdcBias",
	"get HF1-2-iBot_CtrlToSERDES_i2c_write",
	"get HF1-2-B_Bottom_TRST_N",
	"get HF1-2-QIE16_TimingThresholdDAC",
	"get HF1-2-QIE2_IsetpBias",
	"get HF1-2-iBot_DataFromSERDES",
	"get HF1-2-B_CLOCKCOUNTER",
	"get HF1-2-QIE16_Trim",
	"get HF1-2-QIE2_Lvds",
	"get HF1-2-iBot_DataToSERDES",
	"get HF1-2-B_Eic1",
	"get HF1-2-QIE17_CalMode",
	"get HF1-2-QIE2_PedestalDAC",
	"get HF1-2-iBot_FPGA_MAJOR_VERSION",
	"get HF1-2-B_Eic2",
	"get HF1-2-QIE17_CapID0pedestal",
	"get HF1-2-QIE2_RangeSet",
	"get HF1-2-iBot_FPGA_MINOR_VERSION",
	"get HF1-2-B_FIRMVERSION_MAJOR",
	"get HF1-2-QIE17_CapID1pedestal",
	"get HF1-2-QIE2_TGain",
	"get HF1-2-iBot_FPGA_TopOrBottom",
	"get HF1-2-B_FIRMVERSION_MINOR",
	"get HF1-2-QIE17_CapID2pedestal",
	"get HF1-2-QIE2_TimingIref",
	"get HF1-2-iBot_LinkTestMode_BC0Enable",
	"get HF1-2-B_FIRMVERSION_SVN",
	"get HF1-2-QIE17_CapID3pedestal",
	"get HF1-2-QIE2_TimingThresholdDAC",
	"get HF1-2-iBot_LinkTestMode_Enable",
	"get HF1-2-B_GBTX_DataValid",
	"get HF1-2-QIE17_ChargeInjectDAC",
	"get HF1-2-QIE2_Trim",
	"get HF1-2-iBot_LinkTestPattern",
	"get HF1-2-B_GBTX_Override",
	"get HF1-2-QIE17_DiscOn",
	"get HF1-2-QIE3_CalMode",
	"get HF1-2-iBot_OnesRegister",
	"get HF1-2-B_GBTX_ResetB",
	"get HF1-2-QIE17_FixRange",
	"get HF1-2-QIE3_CapID0pedestal",
	"get HF1-2-iBot_RST_QIE_count",
	"get HF1-2-B_GBTX_TxRdy",
	"get HF1-2-QIE17_IdcBias",
	"get HF1-2-QIE3_CapID1pedestal",
	"get HF1-2-iBot_Spy96bits",
	"get HF1-2-B_I2CBUSID",
	"get HF1-2-QIE17_IsetpBias",
	"get HF1-2-QIE3_CapID2pedestal",
	"get HF1-2-iBot_StatFromSERDES_busy",
	"get HF1-2-B_ID1",
	"get HF1-2-QIE17_Lvds",
	"get HF1-2-QIE3_CapID3pedestal",
	"get HF1-2-iBot_StatFromSERDES_i2c_counter",
	"get HF1-2-B_ID2",
	"get HF1-2-QIE17_PedestalDAC",
	"get HF1-2-QIE3_ChargeInjectDAC",
	"get HF1-2-iBot_StatusReg_PLL320MHzLock",
	"get HF1-2-B_JTAGSEL",
	"get HF1-2-QIE17_RangeSet",
	"get HF1-2-QIE3_DiscOn",
	"get HF1-2-iBot_StatusReg_QieDLLNoLock",
	"get HF1-2-B_JTAG_Select_Board",
	"get HF1-2-QIE17_TGain",
	"get HF1-2-QIE3_FixRange",
	"get HF1-2-iBot_UniqueID",
	"get HF1-2-B_JTAG_Select_FPGA",
	"get HF1-2-QIE17_TimingIref",
	"get HF1-2-QIE3_IdcBias",
	"get HF1-2-iBot_WTE_count",
	"get HF1-2-B_ONES",
	"get HF1-2-QIE17_TimingThresholdDAC",
	"get HF1-2-QIE3_IsetpBias",
	"get HF1-2-iBot_ZerosRegister",
	"get HF1-2-B_ONESZEROES",
	"get HF1-2-QIE17_Trim",
	"get HF1-2-QIE3_Lvds",
	"get HF1-2-iBot_fifo_data_1",
	"get HF1-2-B_PulserA_PulsePattern",
	"get HF1-2-QIE18_CalMode",
	"get HF1-2-QIE3_PedestalDAC",
	"get HF1-2-iBot_fifo_data_2",
	"get HF1-2-B_PulserA_TriggerDelay",
	"get HF1-2-QIE18_CapID0pedestal",
	"get HF1-2-QIE3_RangeSet",
	"get HF1-2-iBot_fifo_data_3",
	"get HF1-2-B_PulserA_TriggerSelect",
	"get HF1-2-QIE18_CapID1pedestal",
	"get HF1-2-QIE3_TGain",
	"get HF1-2-iBot_scratch",
	"get HF1-2-B_PulserB_PulsePattern",
	"get HF1-2-QIE18_CapID2pedestal",
	"get HF1-2-QIE3_TimingIref",
	"get HF1-2-iTop_AddrToSERDES",
	"get HF1-2-B_PulserB_TriggerDelay",
	"get HF1-2-QIE18_CapID3pedestal",
	"get HF1-2-QIE3_TimingThresholdDAC",
	"get HF1-2-iTop_CapIdErrLink1_count",
	"get HF1-2-B_PulserB_TriggerSelect",
	"get HF1-2-QIE18_ChargeInjectDAC",
	"get HF1-2-QIE3_Trim",
	"get HF1-2-iTop_CapIdErrLink2_count",
	"get HF1-2-B_RESQIECOUNTER",
	"get HF1-2-QIE18_DiscOn",
	"get HF1-2-QIE4_CalMode",
	"get HF1-2-iTop_CapIdErrLink3_count",
	"get HF1-2-B_SCRATCH",
	"get HF1-2-QIE18_FixRange",
	"get HF1-2-QIE4_CapID0pedestal",
	"get HF1-2-iTop_Clk_count",
	"get HF1-2-B_SHT1_ident",
	"get HF1-2-QIE18_IdcBias",
	"get HF1-2-QIE4_CapID1pedestal",
	"get HF1-2-iTop_CntrReg_CImode",
	"get HF1-2-B_SHT1_rh_f",
	"get HF1-2-QIE18_IsetpBias",
	"get HF1-2-QIE4_CapID2pedestal",
	"get HF1-2-iTop_CtrlToSERDES_i2c_go",
	"get HF1-2-B_SHT1_temp_f",
	"get HF1-2-QIE18_Lvds",
	"get HF1-2-QIE4_CapID3pedestal",
	"get HF1-2-iTop_CtrlToSERDES_i2c_write",
	"get HF1-2-B_SHT1_user",
	"get HF1-2-QIE18_PedestalDAC",
	"get HF1-2-QIE4_ChargeInjectDAC",
	"get HF1-2-iTop_DataFromSERDES",
	"get HF1-2-B_SHT2_ident",
	"get HF1-2-QIE18_RangeSet",
	"get HF1-2-QIE4_DiscOn",
	"get HF1-2-iTop_DataToSERDES",
	"get HF1-2-B_SHT2_rh_f",
	"get HF1-2-QIE18_TGain",
	"get HF1-2-QIE4_FixRange",
	"get HF1-2-iTop_FPGA_MAJOR_VERSION",
	"get HF1-2-B_SHT2_temp_f",
	"get HF1-2-QIE18_TimingIref",
	"get HF1-2-QIE4_IdcBias",
	"get HF1-2-iTop_FPGA_MINOR_VERSION",
	"get HF1-2-B_SHT2_user",
	"get HF1-2-QIE18_TimingThresholdDAC",
	"get HF1-2-QIE4_IsetpBias",
	"get HF1-2-iTop_FPGA_TopOrBottom",
	"get HF1-2-B_Temp_userread",
	"get HF1-2-QIE18_Trim",
	"get HF1-2-QIE4_Lvds",
	"get HF1-2-iTop_LinkTestMode_BC0Enable",
	"get HF1-2-B_Thermometer",
	"get HF1-2-QIE19_CalMode",
	"get HF1-2-QIE4_PedestalDAC",
	"get HF1-2-iTop_LinkTestMode_Enable",
	"get HF1-2-B_Top_TRST_N",
	"get HF1-2-QIE19_CapID0pedestal",
	"get HF1-2-QIE4_RangeSet",
	"get HF1-2-iTop_LinkTestPattern",
	"get HF1-2-B_WTECOUNTER",
	"get HF1-2-QIE19_CapID1pedestal",
	"get HF1-2-QIE4_TGain",
	"get HF1-2-iTop_OnesRegister",
	"get HF1-2-B_ZEROES",
	"get HF1-2-QIE19_CapID2pedestal",
	"get HF1-2-QIE4_TimingIref",
	"get HF1-2-iTop_RST_QIE_count",
	"get HF1-2-Control",
	"get HF1-2-QIE19_CapID3pedestal",
	"get HF1-2-QIE4_TimingThresholdDAC",
	"get HF1-2-iTop_Spy96bits",
#	"get HF1-2-Input",		# This is used for internal debugging.
	"get HF1-2-QIE19_ChargeInjectDAC",
	"get HF1-2-QIE4_Trim",
	"get HF1-2-iTop_StatFromSERDES_busy",
	"get HF1-2-Input_BytesA",
	"get HF1-2-QIE19_DiscOn",
	"get HF1-2-QIE5_CalMode",
	"get HF1-2-iTop_StatFromSERDES_i2c_counter",
	"get HF1-2-Input_BytesBA",
	"get HF1-2-QIE19_FixRange",
	"get HF1-2-QIE5_CapID0pedestal",
	"get HF1-2-iTop_StatusReg_PLL320MHzLock",
	"get HF1-2-Input_BytesBB",
	"get HF1-2-QIE19_IdcBias",
	"get HF1-2-QIE5_CapID1pedestal",
	"get HF1-2-iTop_StatusReg_QieDLLNoLock",
#	"get HF1-2-Output",		# This is used for internal debugging.
	"get HF1-2-QIE19_IsetpBias",
	"get HF1-2-QIE5_CapID2pedestal",
	"get HF1-2-iTop_UniqueID",
	"get HF1-2-Output_Bytes",
	"get HF1-2-QIE19_Lvds",
	"get HF1-2-QIE5_CapID3pedestal",
	"get HF1-2-iTop_WTE_count",
	"get HF1-2-QIE10_CalMode",
	"get HF1-2-QIE19_PedestalDAC",
	"get HF1-2-QIE5_ChargeInjectDAC",
	"get HF1-2-iTop_ZerosRegister",
	"get HF1-2-QIE10_CapID0pedestal",
	"get HF1-2-QIE19_RangeSet",
	"get HF1-2-QIE5_DiscOn",
	"get HF1-2-iTop_fifo_data_1",
	"get HF1-2-QIE10_CapID1pedestal",
	"get HF1-2-QIE19_TGain",
	"get HF1-2-QIE5_FixRange",
	"get HF1-2-iTop_fifo_data_2",
	"get HF1-2-QIE10_CapID2pedestal",
	"get HF1-2-QIE19_TimingIref",
	"get HF1-2-QIE5_IdcBias",
	"get HF1-2-iTop_fifo_data_3",
	"get HF1-2-QIE10_CapID3pedestal",
	"get HF1-2-QIE19_TimingThresholdDAC",
	"get HF1-2-QIE5_IsetpBias",
	"get HF1-2-iTop_scratch",
	"get HF1-2-QIE10_ChargeInjectDAC",
	"get HF1-2-QIE19_Trim",
	"get HF1-2-QIE5_Lvds",
#	"get HF1-2-scan",		# Useless
	"get HF1-2-QIE10_DiscOn",
	"get HF1-2-QIE1_CalMode",
	"get HF1-2-QIE5_PedestalDAC",
	"get HF1-2-vttxBot1-Bias_Current",
	"get HF1-2-QIE10_FixRange",
	"get HF1-2-QIE1_CapID0pedestal",
	"get HF1-2-QIE5_RangeSet",
	"get HF1-2-vttxBot1-Bias_Mask",
	"get HF1-2-QIE10_IdcBias",
	"get HF1-2-QIE1_CapID1pedestal",
	"get HF1-2-QIE5_TGain",
	"get HF1-2-vttxBot1-DIS_ST",
	"get HF1-2-QIE10_IsetpBias",
	"get HF1-2-QIE1_CapID2pedestal",
	"get HF1-2-QIE5_TimingIref",
	"get HF1-2-vttxBot1-ENA",
	"get HF1-2-QIE10_Lvds",
	"get HF1-2-QIE1_CapID3pedestal",
	"get HF1-2-QIE5_TimingThresholdDAC",
	"get HF1-2-vttxBot1-EN_A",
	"get HF1-2-QIE10_PedestalDAC",
	"get HF1-2-QIE1_ChargeInjectDAC",
	"get HF1-2-QIE5_Trim",
	"get HF1-2-vttxBot1-EN_B",
	"get HF1-2-QIE10_RangeSet",
	"get HF1-2-QIE1_DiscOn",
	"get HF1-2-QIE6_CalMode",
	"get HF1-2-vttxBot1-EN_EMA",
	"get HF1-2-QIE10_TGain",
	"get HF1-2-QIE1_FixRange",
	"get HF1-2-QIE6_CapID0pedestal",
	"get HF1-2-vttxBot1-EN_EMB",
	"get HF1-2-QIE10_TimingIref",
	"get HF1-2-QIE1_IdcBias",
	"get HF1-2-QIE6_CapID1pedestal",
	"get HF1-2-vttxBot1-EXTCON",
	"get HF1-2-QIE10_TimingThresholdDAC",
	"get HF1-2-QIE1_IsetpBias",
	"get HF1-2-QIE6_CapID2pedestal",
	"get HF1-2-vttxBot1-MOD",
	"get HF1-2-QIE10_Trim",
	"get HF1-2-QIE1_Lvds",
	"get HF1-2-QIE6_CapID3pedestal",
	"get HF1-2-vttxBot1-Modulation_Mask",
	"get HF1-2-QIE11_CalMode",
	"get HF1-2-QIE1_PedestalDAC",
	"get HF1-2-QIE6_ChargeInjectDAC",
	"get HF1-2-vttxBot1-PREDRV",
	"get HF1-2-QIE11_CapID0pedestal",
	"get HF1-2-QIE1_RangeSet",
	"get HF1-2-QIE6_DiscOn",
	"get HF1-2-vttxBot1-PREHF",
	"get HF1-2-QIE11_CapID1pedestal",
	"get HF1-2-QIE1_TGain",
	"get HF1-2-QIE6_FixRange",
	"get HF1-2-vttxBot1-PREHR",
	"get HF1-2-QIE11_CapID2pedestal",
	"get HF1-2-QIE1_TimingIref",
	"get HF1-2-QIE6_IdcBias",
	"get HF1-2-vttxBot1-PREW",
	"get HF1-2-QIE11_CapID3pedestal",
	"get HF1-2-QIE1_TimingThresholdDAC",
	"get HF1-2-QIE6_IsetpBias",
	"get HF1-2-vttxBot1-PRE_F",
	"get HF1-2-QIE11_ChargeInjectDAC",
	"get HF1-2-QIE1_Trim",
	"get HF1-2-QIE6_Lvds",
	"get HF1-2-vttxBot1-PRE_R",
	"get HF1-2-QIE11_DiscOn",
	"get HF1-2-QIE20_CalMode",
	"get HF1-2-QIE6_PedestalDAC",
	"get HF1-2-vttxBot2-Bias_Current",
	"get HF1-2-QIE11_FixRange",
	"get HF1-2-QIE20_CapID0pedestal",
	"get HF1-2-QIE6_RangeSet",
	"get HF1-2-vttxBot2-Bias_Mask",
	"get HF1-2-QIE11_IdcBias",
	"get HF1-2-QIE20_CapID1pedestal",
	"get HF1-2-QIE6_TGain",
	"get HF1-2-vttxBot2-DIS_ST",
	"get HF1-2-QIE11_IsetpBias",
	"get HF1-2-QIE20_CapID2pedestal",
	"get HF1-2-QIE6_TimingIref",
	"get HF1-2-vttxBot2-ENA",
	"get HF1-2-QIE11_Lvds",
	"get HF1-2-QIE20_CapID3pedestal",
	"get HF1-2-QIE6_TimingThresholdDAC",
	"get HF1-2-vttxBot2-EN_A",
	"get HF1-2-QIE11_PedestalDAC",
	"get HF1-2-QIE20_ChargeInjectDAC",
	"get HF1-2-QIE6_Trim",
	"get HF1-2-vttxBot2-EN_B",
	"get HF1-2-QIE11_RangeSet",
	"get HF1-2-QIE20_DiscOn",
	"get HF1-2-QIE7_CalMode",
	"get HF1-2-vttxBot2-EN_EMA",
	"get HF1-2-QIE11_TGain",
	"get HF1-2-QIE20_FixRange",
	"get HF1-2-QIE7_CapID0pedestal",
	"get HF1-2-vttxBot2-EN_EMB",
	"get HF1-2-QIE11_TimingIref",
	"get HF1-2-QIE20_IdcBias",
	"get HF1-2-QIE7_CapID1pedestal",
	"get HF1-2-vttxBot2-EXTCON",
	"get HF1-2-QIE11_TimingThresholdDAC",
	"get HF1-2-QIE20_IsetpBias",
	"get HF1-2-QIE7_CapID2pedestal",
	"get HF1-2-vttxBot2-MOD",
	"get HF1-2-QIE11_Trim",
	"get HF1-2-QIE20_Lvds",
	"get HF1-2-QIE7_CapID3pedestal",
	"get HF1-2-vttxBot2-Modulation_Mask",
	"get HF1-2-QIE12_CalMode",
	"get HF1-2-QIE20_PedestalDAC",
	"get HF1-2-QIE7_ChargeInjectDAC",
	"get HF1-2-vttxBot2-PREDRV",
	"get HF1-2-QIE12_CapID0pedestal",
	"get HF1-2-QIE20_RangeSet",
	"get HF1-2-QIE7_DiscOn",
	"get HF1-2-vttxBot2-PREHF",
	"get HF1-2-QIE12_CapID1pedestal",
	"get HF1-2-QIE20_TGain",
	"get HF1-2-QIE7_FixRange",
	"get HF1-2-vttxBot2-PREHR",
	"get HF1-2-QIE12_CapID2pedestal",
	"get HF1-2-QIE20_TimingIref",
	"get HF1-2-QIE7_IdcBias",
	"get HF1-2-vttxBot2-PREW",
	"get HF1-2-QIE12_CapID3pedestal",
	"get HF1-2-QIE20_TimingThresholdDAC",
	"get HF1-2-QIE7_IsetpBias",
	"get HF1-2-vttxBot2-PRE_F",
	"get HF1-2-QIE12_ChargeInjectDAC",
	"get HF1-2-QIE20_Trim",
	"get HF1-2-QIE7_Lvds",
	"get HF1-2-vttxBot2-PRE_R",
	"get HF1-2-QIE12_DiscOn",
	"get HF1-2-QIE21_CalMode",
	"get HF1-2-QIE7_PedestalDAC",
	"get HF1-2-vttxBot3-Bias_Current",
	"get HF1-2-QIE12_FixRange",
	"get HF1-2-QIE21_CapID0pedestal",
	"get HF1-2-QIE7_RangeSet",
	"get HF1-2-vttxBot3-Bias_Mask",
	"get HF1-2-QIE12_IdcBias",
	"get HF1-2-QIE21_CapID1pedestal",
	"get HF1-2-QIE7_TGain",
	"get HF1-2-vttxBot3-DIS_ST",
	"get HF1-2-QIE12_IsetpBias",
	"get HF1-2-QIE21_CapID2pedestal",
	"get HF1-2-QIE7_TimingIref",
	"get HF1-2-vttxBot3-ENA",
	"get HF1-2-QIE12_Lvds",
	"get HF1-2-QIE21_CapID3pedestal",
	"get HF1-2-QIE7_TimingThresholdDAC",
	"get HF1-2-vttxBot3-EN_A",
	"get HF1-2-QIE12_PedestalDAC",
	"get HF1-2-QIE21_ChargeInjectDAC",
	"get HF1-2-QIE7_Trim",
	"get HF1-2-vttxBot3-EN_B",
	"get HF1-2-QIE12_RangeSet",
	"get HF1-2-QIE21_DiscOn",
	"get HF1-2-QIE8_CalMode",
	"get HF1-2-vttxBot3-EN_EMA",
	"get HF1-2-QIE12_TGain",
	"get HF1-2-QIE21_FixRange",
	"get HF1-2-QIE8_CapID0pedestal",
	"get HF1-2-vttxBot3-EN_EMB",
	"get HF1-2-QIE12_TimingIref",
	"get HF1-2-QIE21_IdcBias",
	"get HF1-2-QIE8_CapID1pedestal",
	"get HF1-2-vttxBot3-EXTCON",
	"get HF1-2-QIE12_TimingThresholdDAC",
	"get HF1-2-QIE21_IsetpBias",
	"get HF1-2-QIE8_CapID2pedestal",
	"get HF1-2-vttxBot3-MOD",
	"get HF1-2-QIE12_Trim",
	"get HF1-2-QIE21_Lvds",
	"get HF1-2-QIE8_CapID3pedestal",
	"get HF1-2-vttxBot3-Modulation_Mask",
	"get HF1-2-QIE13_CalMode",
	"get HF1-2-QIE21_PedestalDAC",
	"get HF1-2-QIE8_ChargeInjectDAC",
	"get HF1-2-vttxBot3-PREDRV",
	"get HF1-2-QIE13_CapID0pedestal",
	"get HF1-2-QIE21_RangeSet",
	"get HF1-2-QIE8_DiscOn",
	"get HF1-2-vttxBot3-PREHF",
	"get HF1-2-QIE13_CapID1pedestal",
	"get HF1-2-QIE21_TGain",
	"get HF1-2-QIE8_FixRange",
	"get HF1-2-vttxBot3-PREHR",
	"get HF1-2-QIE13_CapID2pedestal",
	"get HF1-2-QIE21_TimingIref",
	"get HF1-2-QIE8_IdcBias",
	"get HF1-2-vttxBot3-PREW",
	"get HF1-2-QIE13_CapID3pedestal",
	"get HF1-2-QIE21_TimingThresholdDAC",
	"get HF1-2-QIE8_IsetpBias",
	"get HF1-2-vttxBot3-PRE_F",
	"get HF1-2-QIE13_ChargeInjectDAC",
	"get HF1-2-QIE21_Trim",
	"get HF1-2-QIE8_Lvds",
	"get HF1-2-vttxBot3-PRE_R",
	"get HF1-2-QIE13_DiscOn",
	"get HF1-2-QIE22_CalMode",
	"get HF1-2-QIE8_PedestalDAC",
	"get HF1-2-vttxTop1-Bias_Current",
	"get HF1-2-QIE13_FixRange",
	"get HF1-2-QIE22_CapID0pedestal",
	"get HF1-2-QIE8_RangeSet",
	"get HF1-2-vttxTop1-Bias_Mask",
	"get HF1-2-QIE13_IdcBias",
	"get HF1-2-QIE22_CapID1pedestal",
	"get HF1-2-QIE8_TGain",
	"get HF1-2-vttxTop1-DIS_ST",
	"get HF1-2-QIE13_IsetpBias",
	"get HF1-2-QIE22_CapID2pedestal",
	"get HF1-2-QIE8_TimingIref",
	"get HF1-2-vttxTop1-ENA",
	"get HF1-2-QIE13_Lvds",
	"get HF1-2-QIE22_CapID3pedestal",
	"get HF1-2-QIE8_TimingThresholdDAC",
	"get HF1-2-vttxTop1-EN_A",
	"get HF1-2-QIE13_PedestalDAC",
	"get HF1-2-QIE22_ChargeInjectDAC",
	"get HF1-2-QIE8_Trim",
	"get HF1-2-vttxTop1-EN_B",
	"get HF1-2-QIE13_RangeSet",
	"get HF1-2-QIE22_DiscOn",
	"get HF1-2-QIE9_CalMode",
	"get HF1-2-vttxTop1-EN_EMA",
	"get HF1-2-QIE13_TGain",
	"get HF1-2-QIE22_FixRange",
	"get HF1-2-QIE9_CapID0pedestal",
	"get HF1-2-vttxTop1-EN_EMB",
	"get HF1-2-QIE13_TimingIref",
	"get HF1-2-QIE22_IdcBias",
	"get HF1-2-QIE9_CapID1pedestal",
	"get HF1-2-vttxTop1-EXTCON",
	"get HF1-2-QIE13_TimingThresholdDAC",
	"get HF1-2-QIE22_IsetpBias",
	"get HF1-2-QIE9_CapID2pedestal",
	"get HF1-2-vttxTop1-MOD",
	"get HF1-2-QIE13_Trim",
	"get HF1-2-QIE22_Lvds",
	"get HF1-2-QIE9_CapID3pedestal",
	"get HF1-2-vttxTop1-Modulation_Mask",
	"get HF1-2-QIE14_CalMode",
	"get HF1-2-QIE22_PedestalDAC",
	"get HF1-2-QIE9_ChargeInjectDAC",
	"get HF1-2-vttxTop1-PREDRV",
	"get HF1-2-QIE14_CapID0pedestal",
	"get HF1-2-QIE22_RangeSet",
	"get HF1-2-QIE9_DiscOn",
	"get HF1-2-vttxTop1-PREHF",
	"get HF1-2-QIE14_CapID1pedestal",
	"get HF1-2-QIE22_TGain",
	"get HF1-2-QIE9_FixRange",
	"get HF1-2-vttxTop1-PREHR",
	"get HF1-2-QIE14_CapID2pedestal",
	"get HF1-2-QIE22_TimingIref",
	"get HF1-2-QIE9_IdcBias",
	"get HF1-2-vttxTop1-PREW",
	"get HF1-2-QIE14_CapID3pedestal",
	"get HF1-2-QIE22_TimingThresholdDAC",
	"get HF1-2-QIE9_IsetpBias",
	"get HF1-2-vttxTop1-PRE_F",
	"get HF1-2-QIE14_ChargeInjectDAC",
	"get HF1-2-QIE22_Trim",
	"get HF1-2-QIE9_Lvds",
	"get HF1-2-vttxTop1-PRE_R",
	"get HF1-2-QIE14_DiscOn",
	"get HF1-2-QIE23_CalMode",
	"get HF1-2-QIE9_PedestalDAC",
	"get HF1-2-vttxTop2-Bias_Current",
	"get HF1-2-QIE14_FixRange",
	"get HF1-2-QIE23_CapID0pedestal",
	"get HF1-2-QIE9_RangeSet",
	"get HF1-2-vttxTop2-Bias_Mask",
	"get HF1-2-QIE14_IdcBias",
	"get HF1-2-QIE23_CapID1pedestal",
	"get HF1-2-QIE9_TGain",
	"get HF1-2-vttxTop2-DIS_ST",
	"get HF1-2-QIE14_IsetpBias",
	"get HF1-2-QIE23_CapID2pedestal",
	"get HF1-2-QIE9_TimingIref",
	"get HF1-2-vttxTop2-ENA",
	"get HF1-2-QIE14_Lvds",
	"get HF1-2-QIE23_CapID3pedestal",
	"get HF1-2-QIE9_TimingThresholdDAC",
	"get HF1-2-vttxTop2-EN_A",
	"get HF1-2-QIE14_PedestalDAC",
	"get HF1-2-QIE23_ChargeInjectDAC",
	"get HF1-2-QIE9_Trim",
	"get HF1-2-vttxTop2-EN_B",
	"get HF1-2-QIE14_RangeSet",
	"get HF1-2-QIE23_DiscOn",
	"get HF1-2-Qie10_ck_ph",
	"get HF1-2-vttxTop2-EN_EMA",
	"get HF1-2-QIE14_TGain",
	"get HF1-2-QIE23_FixRange",
	"get HF1-2-Qie11_ck_ph",
	"get HF1-2-vttxTop2-EN_EMB",
	"get HF1-2-QIE14_TimingIref",
	"get HF1-2-QIE23_IdcBias",
	"get HF1-2-Qie12_ck_ph",
	"get HF1-2-vttxTop2-EXTCON",
	"get HF1-2-QIE14_TimingThresholdDAC",
	"get HF1-2-QIE23_IsetpBias",
	"get HF1-2-Qie13_ck_ph",
	"get HF1-2-vttxTop2-MOD",
	"get HF1-2-QIE14_Trim",
	"get HF1-2-QIE23_Lvds",
	"get HF1-2-Qie14_ck_ph",
	"get HF1-2-vttxTop2-Modulation_Mask",
	"get HF1-2-QIE15_CalMode",
	"get HF1-2-QIE23_PedestalDAC",
	"get HF1-2-Qie15_ck_ph",
	"get HF1-2-vttxTop2-PREDRV",
	"get HF1-2-QIE15_CapID0pedestal",
	"get HF1-2-QIE23_RangeSet",
	"get HF1-2-Qie16_ck_ph",
	"get HF1-2-vttxTop2-PREHF",
	"get HF1-2-QIE15_CapID1pedestal",
	"get HF1-2-QIE23_TGain",
	"get HF1-2-Qie17_ck_ph",
	"get HF1-2-vttxTop2-PREHR",
	"get HF1-2-QIE15_CapID2pedestal",
	"get HF1-2-QIE23_TimingIref",
	"get HF1-2-Qie18_ck_ph",
	"get HF1-2-vttxTop2-PREW",
	"get HF1-2-QIE15_CapID3pedestal",
	"get HF1-2-QIE23_TimingThresholdDAC",
	"get HF1-2-Qie19_ck_ph",
	"get HF1-2-vttxTop2-PRE_F",
	"get HF1-2-QIE15_ChargeInjectDAC",
	"get HF1-2-QIE23_Trim",
	"get HF1-2-Qie1_ck_ph",
	"get HF1-2-vttxTop2-PRE_R",
	"get HF1-2-QIE15_DiscOn",
	"get HF1-2-QIE24_CalMode",
	"get HF1-2-Qie20_ck_ph",
	"get HF1-2-vttxTop3-Bias_Current",
	"get HF1-2-QIE15_FixRange",
	"get HF1-2-QIE24_CapID0pedestal",
	"get HF1-2-Qie21_ck_ph",
	"get HF1-2-vttxTop3-Bias_Mask",
	"get HF1-2-QIE15_IdcBias",
	"get HF1-2-QIE24_CapID1pedestal",
	"get HF1-2-Qie22_ck_ph",
	"get HF1-2-vttxTop3-DIS_ST",
	"get HF1-2-QIE15_IsetpBias",
	"get HF1-2-QIE24_CapID2pedestal",
	"get HF1-2-Qie23_ck_ph",
	"get HF1-2-vttxTop3-ENA",
	"get HF1-2-QIE15_Lvds",
	"get HF1-2-QIE24_CapID3pedestal",
	"get HF1-2-Qie24_ck_ph",
	"get HF1-2-vttxTop3-EN_A",
	"get HF1-2-QIE15_PedestalDAC",
	"get HF1-2-QIE24_ChargeInjectDAC",
	"get HF1-2-Qie2_ck_ph",
	"get HF1-2-vttxTop3-EN_B",
	"get HF1-2-QIE15_RangeSet",
	"get HF1-2-QIE24_DiscOn",
	"get HF1-2-Qie3_ck_ph",
	"get HF1-2-vttxTop3-EN_EMA",
	"get HF1-2-QIE15_TGain",
	"get HF1-2-QIE24_FixRange",
	"get HF1-2-Qie4_ck_ph",
	"get HF1-2-vttxTop3-EN_EMB",
	"get HF1-2-QIE15_TimingIref",
	"get HF1-2-QIE24_IdcBias",
	"get HF1-2-Qie5_ck_ph",
	"get HF1-2-vttxTop3-EXTCON",
	"get HF1-2-QIE15_TimingThresholdDAC",
	"get HF1-2-QIE24_IsetpBias",
	"get HF1-2-Qie6_ck_ph",
	"get HF1-2-vttxTop3-MOD",
	"get HF1-2-QIE15_Trim",
	"get HF1-2-QIE24_Lvds",
	"get HF1-2-Qie7_ck_ph",
	"get HF1-2-vttxTop3-Modulation_Mask",
	"get HF1-2-QIE16_CalMode",
	"get HF1-2-QIE24_PedestalDAC",
	"get HF1-2-Qie8_ck_ph",
	"get HF1-2-vttxTop3-PREDRV",
	"get HF1-2-QIE16_CapID0pedestal",
	"get HF1-2-QIE24_RangeSet",
	"get HF1-2-Qie9_ck_ph",
	"get HF1-2-vttxTop3-PREHF",
	"get HF1-2-QIE16_CapID1pedestal",
	"get HF1-2-QIE24_TGain",
	"get HF1-2-Status",
	"get HF1-2-vttxTop3-PREHR",
	"get HF1-2-QIE16_CapID2pedestal",
	"get HF1-2-QIE24_TimingIref",
	"get HF1-2-UniqueID",
	"get HF1-2-vttxTop3-PREW",
	"get HF1-2-QIE16_CapID3pedestal",
	"get HF1-2-QIE24_TimingThresholdDAC",
	"get HF1-2-UniqueIDn",
	"get HF1-2-vttxTop3-PRE_F",
	"get HF1-2-QIE16_ChargeInjectDAC",
	"get HF1-2-QIE24_Trim",
	"get HF1-2-bkp_pwr_bad",
	"get HF1-2-vttxTop3-PRE_R",
	"get HF1-2-QIE16_DiscOn",
	"get HF1-2-QIE2_CalMode",
	"get HF1-2-bkp_temp_f",
	"get HF1-adc50_control",
	"get HF1-adc50temp_f",
	"get HF1-adc52_t",
	"get HF1-adc54_f",
	"get HF1-adc56_control",
	"get HF1-adc56temp_f",
	"get HF1-adc58_t",
	"get HF1-adc50_f",
	"get HF1-adc52_control",
	"get HF1-adc52temp_f",
	"get HF1-adc54_t",
	"get HF1-adc56_f",
	"get HF1-adc58_control",
	"get HF1-adc58temp_f",
	"get HF1-adc50_t",
	"get HF1-adc52_f",
	"get HF1-adc54_control",
	"get HF1-adc54temp_f",
	"get HF1-adc56_t",
	"get HF1-adc58_f",
	"get HF1-adc5Atemp_f",
	"get HF1-bitslip_ctrl_slide_enable",
	"get HF1-bkp_pwr_bad",
	"get HF1-bkpregs_ngccm_bkp_reset_out",
	"get HF1-bkpregs_ngccm_rev_id",
	"get HF1-bitslip_ctrl_slide_manual",
	"get HF1-bkpregs_bkp_pwr_good",
	"get HF1-bkpregs_ngccm_bkp_reset_qie_out",
	"get HF1-bitslip_ctrl_slide_nbr",
	"get HF1-bkpregs_bkp_spare",
	"get HF1-bkpregs_ngccm_bkp_wte_out",
	"get HF1-bitslip_ctrl_slide_run",
	"get HF1-bkpregs_ngccm_bkp_pwr_enable_out",
	"get HF1-bkpregs_ngccm_neigh_rev_id",
	"get HF1-BERCLK",
	"get HF1-directaccess",
	"get HF1-gbt_status_aligned",
	"get HF1-gbt_status_bitslips",
	"get HF1-heartbeat_enabled",
	"get HF1-jtag_data",
	"get HF1-jtag_reg",
	"get HF1-jtag_sel",
	"get HF1-link_ctrl_gbt_rx_rst",
	"get HF1-link_ctrl_gtx_loopback",
	"get HF1-link_ctrl_gtx_rx_reset",
	"get HF1-link_ctrl_gtx_tx_pwrdown",
	"get HF1-link_ctrl_gtx_tx_sync_rst",
	"get HF1-link_ctrl_gbt_tx_rst",
	"get HF1-link_ctrl_gtx_rx_pwrdown",
	"get HF1-link_ctrl_gtx_rx_sync_rst",
	"get HF1-link_ctrl_gtx_tx_reset",
	"get HF1-m-Control",
#	"get HF1-m-scan",		# Useless
	"get HF1-m-vtrx-EN_EMB",
	"get HF1-m-vtrx-PRE_F",
	"get HF1-mezz_SERDES_LANE_SEL",
#	"get HF1-m-Input",		# This is used for internal debugging.
	"get HF1-m-vtrx-Bias_Current",
	"get HF1-m-vtrx-EXTCON",
	"get HF1-m-vtrx-PRE_R",
	"get HF1-mezz_SERDES_REFCLK_SEL",
	"get HF1-m-Input_BytesA",
	"get HF1-m-vtrx-Bias_Mask",
	"get HF1-m-vtrx-MOD",
	"get HF1-mezz_BoardID",
	"get HF1-mezz_ZEROES",
	"get HF1-m-Input_BytesBA",
	"get HF1-m-vtrx-DIS_ST",
	"get HF1-m-vtrx-Modulation_Mask",
	"get HF1-mezz_ERROR_COUNT",
	"get HF1-mezz_error_count_reset",
	"get HF1-m-Input_BytesBB",
	"get HF1-m-vtrx-ENA",
	"get HF1-m-vtrx-PREDRV",
	"get HF1-mezz_FPGA_MAJOR_VERSION",
	"get HF1-mezz_reg3",
#	"get HF1-m-Output",		# This is used for internal debugging.
	"get HF1-m-vtrx-EN_A",
	"get HF1-m-vtrx-PREHF",
	"get HF1-mezz_FPGA_MINOR_VERSION",
	"get HF1-mezz_scratch",
	"get HF1-m-Output_Bytes",
	"get HF1-m-vtrx-EN_B",
	"get HF1-m-vtrx-PREHR",
	"get HF1-mezz_ONES",
	"get HF1-mezz_slowSig1",
	"get HF1-m-Status",
	"get HF1-m-vtrx-EN_EMA",
	"get HF1-m-vtrx-PREW",
	"get HF1-mezz_RX_BITSLIP_NUMBER",
	"get HF1-mezz_slowSig2",
	"get HF1-n-Control",
	"get HF1-n-Input_BytesA",
	"get HF1-n-Input_BytesBB",
	"get HF1-n-Output_Bytes",
#	"get HF1-n-scan",		# Useless.
#	"get HF1-n-Input",		# This is used for internal debugging.
	"get HF1-n-Input_BytesBA",
#	"get HF1-n-Output",		# This is used for internal debugging.
	"get HF1-n-Status",
	"get HF1-power",
	"get HF1-pulser-daccontrol_ToggleFunctionEnable",
	"get HF1-pulser-delay-cr3_delay",
	"get HF1-pulser-daccontrol_ChannelMonitorEnable",
	"get HF1-pulser-delay-cr0_delay",
	"get HF1-pulser-delay-cr3_enable",
	"get HF1-pulser-daccontrol_CurrentBoostEnable",
	"get HF1-pulser-delay-cr0_enable",
	"get HF1-pulser-delay-cr4_delay",
	"get HF1-pulser-daccontrol_InternalRefEnable",
	"get HF1-pulser-delay-cr1_delay",
	"get HF1-pulser-delay-cr4_enable",
	"get HF1-pulser-daccontrol_PowerDownStatus",
	"get HF1-pulser-delay-cr1_enable",
	"get HF1-pulser-delay-gcr_IDLL",
	"get HF1-pulser-daccontrol_RefSelect",
	"get HF1-pulser-delay-cr2_delay",
	"get HF1-pulser-delay-gcr_freq",
	"get HF1-pulser-daccontrol_ThermalMonitorEnable",
	"get HF1-pulser-delay-cr2_enable",
	"get HF1-pwrenable",
	"get HF1-qiereset",
	"get HF1-reset",
	"get HF1-RX_40MHZ",
	"get HF1-RX_USRCLK_DIV2",
	"get HF1-TX_40MHZ",
	"get HF1-TX_USRCLK_DIV2",
	"get HF1-vtrx_clk_rssi_f",
	"get HF1-vtrx_rssi_f",
	"get HF1-VIN_current_f",
	"get HF1-VIN_voltage_f",
	"get HF1-wte",
	"get fec1-BC0_cnt",
	"get fec1-firmware_dd",
	"get fec1-gbt_phase_mon_reset",
	"get fec1-sfp1_status.TxFault",
	"get fec1-tclka_dr_en",
	"get fec1-v6_cpld",
	"get fec1-DbErr_cnt",
	"get fec1-firmware_mm",
	"get fec1-gtx_conf",
	"get fec1-sfp2_status.Mod_abs",
	"get fec1-tclkb_dr_en",
	"get fec1-xpoint_2x2_s1",
	"get fec1-EC0_cnt",
	"get fec1-firmware_ver_build",
	"get fec1-gtx_global_reset",
	"get fec1-sfp2_status.RxLOS",
	"get fec1-user_board_id",
	"get fec1-xpoint_2x2_s2",
	"get fec1-LHC_clk_freq",
	"get fec1-firmware_ver_major",
	"get fec1-icap_page",
	"get fec1-sfp2_status.TxFault",
	"get fec1-user_firmware_dd",
	"get fec1-xpoint_4x4_s1",
	"get fec1-SinErr_cnt",
	"get fec1-firmware_ver_minor",
	"get fec1-icap_trigg",
	"get fec1-sfp3_status.Mod_abs",
	"get fec1-user_firmware_mm",
	"get fec1-xpoint_4x4_s2",
	"get fec1-board_id",
	"get fec1-firmware_yy",
	"get fec1-pcie_clk_fsel",
	"get fec1-sfp3_status.RxLOS",
	"get fec1-user_firmware_yy",
	"get fec1-xpoint_4x4_s3",
	"get fec1-cdce_ctrl_sel",
	"get fec1-fmc1_presence",
	"get fec1-pcie_clk_mr",
	"get fec1-sfp3_status.TxFault",
	"get fec1-user_sys_id",
	"get fec1-xpoint_4x4_s4",
	"get fec1-cdce_lock",
	"get fec1-fmc2_presence",
	"get fec1-pcie_clk_oe",
	"get fec1-sfp4_status.Mod_abs",
	"get fec1-user_ver_build",
	"get fec1-cdce_powerup",
	"get fec1-fpga_program_b_trst",
	"get fec1-qie_reset_cnt",
	"get fec1-sfp4_status.RxLOS",
	"get fec1-user_ver_major",
	"get fec1-cdce_refsel",
	"get fec1-fpga_reset",
	"get fec1-sfp1_status.Mod_abs",
	"get fec1-sfp4_status.TxFault",
	"get fec1-user_ver_minor",
	"get fec1-cdce_sync",
	"get fec1-gbe_int",
	"get fec1-sfp1_status.RxLOS",
	"get fec1-sma_output",
	"get fec1-user_wb_regs",
	"get softf1",
	"get softf2u",
	"get softf3s",
	"get testsoft",
	"get testsoft32",
	"get testsoftread","get HF1-1wA_config",
	"get HF1-1wA_id",
	"get HF1-1wA_user1",
	"get HF1-1wB_config",
	"get HF1-1wB_id",
	"get HF1-1wB_user1",
	"get HF1-1wA_f",
	"get HF1-1wA_t",
	"get HF1-1wA_user2",
	"get HF1-1wB_f",
	"get HF1-1wB_t",
	"get HF1-1wB_user2",
	"get HF1-tmr_errors",
	"get HF1-tmr_errors2",
]
# /VARIABLES

if __name__ == "__main__":
	print "Hang on."
	print 'What you just ran is "ngccm.py". This is a module, not a script. See the documentation ("readme.md") for more information.'
