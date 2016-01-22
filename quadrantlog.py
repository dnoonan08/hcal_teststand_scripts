####################################################################
# Type: SCRIPT                                                     #
#                                                                  #
# Description: This script logs all BRIDGE, IGLOO2, and nGCCM      #
# registers as well as the power supply and time. This script is   #
# to run continuously, logging at a user set period.               #
####################################################################

from hcal_teststand import *
from hcal_teststand.hcal_teststand import teststand
from hcal_teststand.utilities import *
import sys
import os
from optparse import OptionParser
from time import sleep,strftime
import numpy
from commands import getoutput
from sqlite3 import *
# CLASSES:
# /CLASSES

# FUNCTIONS:
def log_temp(ts,c=False):
	if c:
		tm=time_string()[:-4]
		c.execute('create table if not exists temperature (time text, cmd text, temp real)')
	log = ""
	try:
		temps = hcal_teststand.get_temps(ts).values()		# Only care about crate 1
	except Exception as ex:
		print ex
		temps = False
	log += "%% TEMPERATURES\n"
	if temps:
		for results in temps:
			for result in results:
				log += "{0} -> {1}\n".format(result["cmd"], result["result"])
				if c: c.execute("INSERT INTO temperature VALUES ('{0}','{1}',{2})".format(tm,result['cmd'][4:],result['result'] if 'ERROR!' not in result['result'] else -1))
	crates=ts.fe_crates
	cmds=[]
	for crate in crates:
		cmds.extend([
				"get HF{0}-adc58_f".format(crate),		# Check that this is less than 65.
				"get HF{0}-1wA_f".format(crate),
				"get HF{0}-1wB_f".format(crate),
				])
  	output = ngfec.send_commands(ts=ts,control_hub=ts.control_hub, cmds=cmds)
	for result in output:
		log += "{0} -> {1}\n".format(result["cmd"], result["result"])
		if c: c.execute("INSERT INTO temperature VALUES ('{0}','{1}',{2})".format(tm,result['cmd'][4:],result['result'] if 'ERROR!' not in result['result'] else -1))
	return log

def log_power(ts,c=False):
	if c:
		tm=time_string()[:-4]
		c.execute('create table if not exists power (time text, cmd text, value real)')
	log = "%% POWER\n"
#	power_fe = ts_157.get_power(ts)
#	log += "%% POWER\n{0:.2f} V\n{1:.2f} A\n".format(power_fe["V"], power_fe["I"])
	try:
		power_ngccm = ngccm.get_power(ts)		# Take only the crate 1 results (there's only one crate, anyway).
	except Exception as ex:
		print ex
		power_ngccm = {}
	for cra in power_ngccm.keys():
		for result in power_ngccm[cra]:
			log += "{0} -> {1}\n".format(result["cmd"], result["result"])
			if c: c.execute("INSERT INTO power VALUES ('{0}','{1}',{2})".format(tm,result['cmd'][4:],result['result'] if 'ERROR!' not in result['result'] else -1))
	return log

def log_link(ts,erro):
	log = "%% LINK\n"
	err=''
	uips=ts.uhtr_ips
	for cs in uips:
		raw=uhtr.get_raw_status(ip=uips[cs]).values()[0].split('\n')
		links=[]
		baddata=[]
		rollc=[]
		for l in raw:
			if 'BadCounter' in l: links.extend(l.split('BadCounter')[-1].split())
			if 'Bad Data' in l: baddata.extend(l.split('Bad Data')[-1].split())
			if 'Rollover Count' in l: rollc.extend(l.split('Rollover Count')[-1].split())
		if links != ['ON']*24: err+='link status: {0} for BE{1}\n'.format(links,cs)
#		if baddata != ['0']*24: err+='Bad data: {0} for BE{1}\n'.format(baddata,cs)
		log+='link status: {0} for BE{1}\n'.format(links,cs)
		log+='Bad data: {0} for BE{1}\n'.format(baddata,cs)
		log+='Rollover Count: {0} for BE{1}\n'.format(rollc,cs)
#	if err: erro['link']=err
	return log
		
		
def bkp_reset(ts):
	cmds=[]
	crates=ts.fe_crates
	for crate in crates:
		cmds.append('put HF{0}-bkp_reset 1'.format(crate))
		cmds.append('put HF{0}-bkp_reset 0'.format(crate))
	output=ngfec.send_commands(ts=ts,control_hub=ts.control_hub, cmds=cmds)
	for result in output:
		print ">> {0} -> {1}".format(result["cmd"], result["result"])
	
adcorder=[8,0,11,3,10,2,9,1]
tdcorder=[14,6,13,5,12,4]
def log_igloo(ts,c=False):
	if c:
		tm=time_string()[:-4]
		c.execute('create table if not exists igloospy (time text, crate integer, slot integer, cmd text, indx integer, channel integer, capid integer, adc integer, tdc integer )')
	log=''
	error=''
	nslots=ts.qie_slots
	crates=ts.fe_crates
	for n in range(len(crates)):
		crate=crates[n]
		nslot=nslots[n]
		for i in nslot:
			cmds=["put HF{0}-{1}-iTop_CntrReg_WrEn_InputSpy 1".format(crate,i),
			      "put HF{0}-{1}-iTop_CntrReg_WrEn_InputSpy 0".format(crate,i),
			      "put HF{0}-{1}-iBot_CntrReg_WrEn_InputSpy 1".format(crate,i),
			      "put HF{0}-{1}-iBot_CntrReg_WrEn_InputSpy 0".format(crate,i),
			      ]
			cmds.extend(["get HF{0}-{1}-iTop_inputSpy".format(crate,i)]*12)
			cmds.extend(["get HF{0}-{1}-iBot_inputSpy".format(crate,i)]*12)
			output = ngfec.send_commands(ts=ts,control_hub=ts.control_hub, cmds=cmds)
			ind=0
			for result in output:
				if result["cmd"][:3]=='put':
					if result["result"]=='OK':continue
					else:
						error+="ERROR: {0} -> {1}\n".format(result["cmd"], result["result"])
						break
				if result["cmd"][:3]=='get':
					ind=ind%12+1
					if 'ERROR!' in result["result"]:
						error+="ERROR: {0} (Spy{2}) -> {1} \n".format(result["cmd"], result["result"],ind)
						continue
					log+='{0} (Spy{1}) ->\n'.format(result['cmd'],ind)
					hexdc=result['result'].split()[1:]
					bindc=[]
					for deco in hexdc:
						if len(deco)>6:
							bindc.append(bin(int(deco[:-4],16))[2:])
							bindc.append(bin(int(deco[-4:],16))[2:])
						else:
							bindc.append('')
							bindc.append(bin(int(deco,16))[2:])

					cha=0
					for deco in bindc:
						cha+=1
						deco='0'*(16-len(deco))+deco
						adc=''
						tdc=''
						for ii in adcorder:
							adc+=deco[15-ii]
						for ii in tdcorder:
							tdc+=deco[15-ii]
						capid=deco[0]+deco[8]
						log+="\tchannel:{0}\tcapid:{1}\tadc:{2}\ttdc:{3}\n".format(cha,int(capid,2),int(adc,2),int(tdc,2))
						if c: c.execute("INSERT INTO igloospy VALUES ('{0}',{1},{2},'{3}',{4},{5},{6},{7},{8})".format(tm,crate,i,result['cmd'].split('-')[-1],ind,cha,int(capid,2),int(adc,2),int(tdc,2)))
	log=error+log
	log="%% IGLOOSPY\n"+log
	return log

def log_registers(ts,c=False, scale=0):		# Scale 0 is the sparse set of registers, 1 is full.
	if c:
		tm=time_string()[:-4]
		c.execute('create table if not exists register (time text, cmd text, value text)')
	log = ""
	log += "%% REGISTERS\n"
	nslots=ts.qie_slots
	crates=ts.fe_crates
	cmds=[]
	for n in range(len(crates)):
		crate=crates[n]
		nslot=nslots[n]
		if scale == 0:
			cmds.extend( [
				"get HF{0}-mezz_ONES".format(crate),		# Check that this is all 1s.
				"get HF{0}-mezz_ZEROES".format(crate),		# Check that is is all 0s.
				"get HF{0}-bkp_pwr_bad".format(crate),
				"get HF{0}-mezz_TMR_ERROR_COUNT".format(crate),
				"get HF{0}-mezz_FPGA_MAJOR_VERSION".format(crate),
				"get HF{0}-mezz_FPGA_MINOR_VERSION".format(crate),
				"get HF{0}-mezz_rx_prbs_error_cnt".format(crate),
				"get HF{0}-fec_rx_prbs_bitwise_error_cnt HF{0}-fec_rx_prbs_error_cnt".format(crate),
				])
			
			for i in nslot:
				cmds.append("get HF{0}-{1}-B_RESQIECOUNTER".format(crate,i))
				cmds.append("get HF{0}-{1}-B_RESQIECOUNTER".format(crate,i))
				cmds.append("get HF{0}-{1}-iTop_RST_QIE_count".format(crate,i))
				cmds.append("get HF{0}-{1}-iTop_RST_QIE_count".format(crate,i))
				cmds.append("get HF{0}-{1}-iBot_RST_QIE_count".format(crate,i))
				cmds.append("get HF{0}-{1}-iBot_RST_QIE_count".format(crate,i))
#				cmds.append("get HF{0}-{1}-iTop_LinkTestMode".format(crate,i))
#				cmds.append("get HF{0}-{1}-iBot_LinkTestMode".format(crate,i))
#				cmds.append("get HF{0}-{1}-iTop_CntrReg_CImode".format(crate,i))
#				cmds.append("get HF{0}-{1}-iBot_CntrReg_CImode".format(crate,i))
		elif scale == 1:
			for i in nslot:
				cmds.extend(ngccm.get_commands(crate,i))
#	cmds.extend(["get fec1-sfp{0}_prbs_rx_pattern_error_cnt".format(m+1) for m in range(6)])
#	cmds.extend(["get fec2-sfp{0}_prbs_rx_pattern_error_cnt".format(m+1) for m in range(2)])
	if scale == 0:
		cmds.extend([
				"get fec1-LHC_clk_freq",		# Check that this is > 400776 and < 400788.
				"get fec1-qie_reset_cnt",
				"get fec1-firmware_dd",
				"get fec1-firmware_mm",
				"get fec1-firmware_yy",
				"get fec1-sfp1_status.RxLOS",
				])
#	cmds=list(set(cmds))
	output = ngfec.send_commands(ts=ts,control_hub=ts.control_hub, cmds=cmds)
	for result in output:
		log += "{0} -> {1}\n".format(result["cmd"], result["result"])
		if c: c.execute("INSERT INTO power VALUES ('{0}','{1}','{2}')".format(tm,result['cmd'][4:],result['result']))
	return log
	
def record(ts=False,c=False,path="data/unsorted", scale=0):
	log = ""
	err={}
	t_string = time_string()[:-4]
	t0 = time_string()

	# Log basics:
	log += log_power(ts,c)		# Power
	log += "\n"
#	log += log_version(ts)
	log += log_temp(ts,c)		# Temperature
	log += "\n"
	log += '%% USERS\n'
	log += getoutput('w')
	log += "\n"
	log += "\n"
	# Log registers:
	log += log_registers(ts=ts, c=c, scale=scale,)
	log += "\n"
	
	# Log link:
	log += log_link(ts,err)
	log += "\n"

	# Log igloo:
	log += log_igloo(ts,c)
	log += "\n"
	
	# Log other:
#	log += "[!!]%% WHAT?\n(There is an error counter, which I believe is in the I2C register. This only counts GBT errors from GLIB to ngCCM. I doubt that Ozgur has updated the GLIB v3 to also count errors from ngCCM to GLIB. That would be useful to have if the counter exists.\nI also want to add, if there is time, an error counter of TMR errors. For the DFN macro TMR code, I implement an error output that goes high if all three outputs are not the same value. This would monitor only a couple of D F/Fs but I think it would be useful to see if any TMR errors are detected.)\n\n"

	# Time:
	t1 = time_string()
	log = "%% TIMES\n{0}\n{1}\n\n".format(t0, t1) + log
	isreg=[line for line in log.split('%% IGLOOSPY\n')[0].split('\n') if '->' in line]
	badrate=len([line for line in isreg if 'ERROR!!' in line])*100/len(isreg)
	if badrate>50:err['register']='logger on hcal904daq01 cannot read registers, bad register rate: {0}%'.format(badrate)
	errs='\n'.join(err.values())
	if errs:	os.system("ssh cms904usr mail -s 'logger_information' yw5mj@virginia.edu jmariano@terpmail.umd.edu whitbeck.andrew@gmail.com<<EOF\nERROR in {0}.log:\n\n{1}\nEOF".format(t_string,errs))
	# Write log:
	path += "/{0}".format(t_string[:-7])
	scale_string = ""
	if scale == 0:
		scale_string = "sparse"
	elif scale == 1:
		scale_string = "full"
	print ">> {0}: Created a {1} log file named \"{2}.log\" in directory \"{3}\"".format(t1[:-4], scale_string, t_string, path)
	if not os.path.exists(path):
		os.makedirs(path)
	with open("{0}/{1}.log".format(path, t_string), "w") as out:
		out.write(log.strip())
	if c: conn.commit()
	return log
# /FUNCTIONS

# MAIN:
if __name__ == "__main__":
	# Script arguments:
	parser = OptionParser()
	parser.add_option("-t", "--teststand", dest="ts",
		default="904",
		help="The name of the teststand you want to use (default is \"904\"). Unless you specify the path, the directory will be put in \"data\".",
		metavar="STR"
	)
	parser.add_option("-o", "--fileName", dest="out",
		default="",
		help="The name of the directory you want to output the logs to (default is \"ts_904\").",
		metavar="STR"
	)
	parser.add_option("-s", "--sparse", dest="spar",
		default=1,
		help="The sparse logging period in minutes (default is 1).",
		metavar="FLOAT"
	)
	parser.add_option("-f", "--full", dest="full",
		default=0,
		help="The bkp_reset period in days (default is 0).",
		metavar="FLOAT"
	)
	parser.add_option("-T", "--time", dest="ptime",
		default='',
		help="The full logging time in a day (default is empty).",
		metavar="STR"
	)
	parser.add_option("-D", "--dd", dest="db",
			  default=True, action='store_false',
			  help='disable database.'
			  )
	(options, args) = parser.parse_args()
	name = options.ts
	period = float(options.spar)
	if not options.out:
		path = "data/ts_{0}".format(name)
	elif "/" in options.out:
		path = options.out
	else:
		path = "data/" + options.out
	c=False
	if options.db:
		os.system('mkdir -p '+path)
		conn=connect(path+'/logger.db')
		c=conn.cursor()

	period_long = float(options.full)
	
	# Set up teststand:
	ts = teststand(name)
	
	# Print information:
	print ">> The output directory is {0}.".format(path)
	print ">> The logging period is {0} minutes.".format(period)
	print ">> (A BackPlane reset signal will be sent every {0} days.)".format(period_long)
	if c: print ">> Writing to database {0}/logger.db.".format(path)
	# Logging loop:
	z = True
	t0 = 0
	t0_long = 0
	while z == True:
		dt = time.time() - t0
		dt_long = time.time() - t0_long
		if (period_long!=0) and (dt_long > period_long*86400):
			t0_long = time.time()
			bkp_reset(ts)
		if (period!=0) and (dt > period*60):
			t0 = time.time()
			record(ts=ts,c=c, path=path, scale=0)
		if strftime("%H:%M") == options.ptime:
			record(ts=ts,c=c, path=path, scale=1)
		else:
			sleep(1)
#		z = False
	
# /MAIN
