from hcal_teststand import *
from hcal_teststand.hcal_teststand import teststand 
import sys
import random
import os
from fnmatch import fnmatch

def Check_SW(verbose, ts):
	print "*********************************************"
	print "Checking the counting room switch statuses..."
	print "*********************************************"

	commands = "get HF2-ngccm_slow2reg_CountingRoomJumper[1-4]"

	errors = []
	results = ngccm.send_commands_parsed( ts, commands)
	if verbose == 1:
		for i in range(1,5):
			print "SW" + str(i) + ": " + results['output'][0]['result'].split()[i-1]
			if results['output'][0]['result'].split()[i-1] != "1":
				errors.append([i,results['output'][0]['result'].split()[i-1]])
	
	if results['output'][0]['result'] == "1 1 1 1":
		print "***************************************"
		print "All counting room switches look normal."
		print "***************************************"
		return 0
	else:
		print "******************************************************"
		print str(len(errors)) + " switches seem to have an unexpected value:"
		print "******************************************************"
		for i in range (0,len(errors)):
			print "SW" + str(errors[i][0]) + ": " + errors[i][1]
		print "******************************************************"
		return len(errors)

def get_SN():
	SN = raw_input("Enter ngCCM SN: ")
	return SN

def ADCs(verbose,ts):
        adcs_file = open('adcs')
        adc_registers = adcs_file.readlines()
        adcs_file.close()

        commands = []
        for i in range(0,len(adc_registers)):
                commands.append("get " + adc_registers[i].rstrip())

        print "*************************"
        print "Reading mezzanine ADCs..."
        print "*************************"

        results = ngccm.send_commands_parsed( ts, commands)
	warnings = []
	for i in range(0,len(results['output'])):
		if fnmatch(results['output'][i]['result'],"ERROR!!  I2C: NACK") == 1:
			warnings.append([i,3,results['output'][i]['result']])
		elif i < 6:
			if verbose == 1:
				print "ADC" + str(i+1) + ":   " + results['output'][i]['result'] + " C"
			if float(results['output'][i]['result']) < 15:
				warnings.append([i,0,results['output'][i]['result']])
			if float(results['output'][i]['result']) > 45:
				warnings.append([i,1,results['output'][i]['result']])
			if float(results['output'][i]['result']) > 55:
				warnings.append([i,2,results['output'][i]['result']])
		elif i == 6:
			if verbose == 1:
				print "ADC" + str(i+1) + ":   " + results['output'][i]['result'] + " A"
			if (float(results['output'][i]['result']) < 1.4) or (float(results['output'][i]['result']) > 1.55):
				warnings.append([i,-1,results['output'][i]['result']])
		elif i == 7:
			if verbose == 1:
				print "ADC" + str(i+1) + ":   " + results['output'][i]['result'] + " V"
			if (float(results['output'][i]['result']) < 7.8) or (float(results['output'][i]['result']) > 8.2):
				warnings.append([i,-1,results['output'][i]['result']])

	if len(warnings) == 0:
		print "********************"
		print "All ADCs look normal"
		print "********************"
		return 0
	else:
		print "**********************************"
		print str(len(warnings)) + " ADCs may be in error:"
		print "**********************************" 
		for i in range(0,len(warnings)):
			if warnings[i][1] == 3:
				print "Error reading ADC" + str(warnings[i][0]) + ": " + warnings[i][2]
			elif warnings[i][0] < 6:
				if warnings[i][1] == 0:
					print "ADC" + str(warnings[i][0]+1) + ":   " + warnings[i][2] + "C     This looks to cold. There may be a problem with the ADC."
				if warnings[i][1] == 1:
					print "ADC" + str(warnings[i][0]+1) + ":   " + warnings[i][2] + "C     Warning! This is pretty hot. Is the ngCCM properly ventilated?"
				if warnings[i][1] == 2:
					print "ADC" + str(warnings[i][0]+1) + ":   " + warnings[i][2] + "C     This is too hot! Power down the board immediatedly!"
			elif warnings[i][0] == 6:
				print "ADC" + str(warnings[i][0]+1) + ":   " + warnings[i][2] + " A     This current does not look right. The expected value is ~1.6A"
			elif warnings[i][0] == 7:
				print "ADC" + str(warnings[i][0]+1) + ":   " + warnings[i][2] + " V     This value does not look right. The expected value is ~8.0V"
		print "**********************************"
		return len(warnings)

def QIEs(number,verbose,ts,slots):
        print "*****************************************"
        print "Testing the QIE scratch registers..."
        print "*****************************************"

        random.seed()

	total_write_failures = 0
	total_read_failures = 0
	total_both_failures = 0
	for n in slots:
		commands = []
		rand_ints = []
		rand_hexes = []
		for i in range(0,number):
			rand_ints.append(random.randint(10,int(0xffffffff)))
			rand_hexes.append(str(hex(rand_ints[i])))
			commands.append("put HF2-" + str(n) + "-B_SCRATCH " + str(rand_ints[i]))
			commands.append("get HF2-" + str(n) + "-B_SCRATCH")

			results = ngccm.send_commands_parsed( ts, commands)
			failures = []
			write_failures = 0
			read_failures = 0
			both_failures = 0	
			for i in range(0,len(results['output'])/2):
				if (results['output'][2*i]['result'] == "OK") and (results['output'][(2*i)+1]['result'] == rand_hexes[i]):
					if verbose == 1:
						print "Write pattern: " + rand_hexes[i] + ":     Write: Passed (" + results['output'][2*i]['result'] + ")     Read: Passed (" + results['output'][(2*i)+1]['result'] + ")"
				elif results['output'][2*i]['result'] == "OK":
					if verbose == 1:
						print "Write pattern: " + rand_hexes[i] + ":     Write: Passed (" + results['output'][2*i]['result'] + ")     Read: FAILED (" + results['output'][(2*i)+1]['result'] + ")"
					failures.append([1,rand_hexes[i],results['output'][2*i]['result'],results['output'][(2*i)+1]['result']])
					read_failures += 1
				elif results['output'][(2*i)+1]['result'] == rand_hexes[i]:
					if verbose == 1:
						print "Write pattern: " + rand_hexes[i] + ":     Write: FAILED (" + results['output'][2*i]['result'] + ")     Read: Passed (" + results['output'][(2*i)+1]['result'] + ")"
					failures.append([0,rand_hexes[i],results['output'][2*i]['result'],results['output'][(2*i)+1]['result']])
					write_failures += 1
				else:
					if verbose == 1:
						print "Write pattern: " + rand_hexes[i] + ":     Write: FAILED (" + results['output'][2*i]['result'] + ")     Read: FAILED (" + results['output'][(2*i)+1]['result'] + ")"
					failures.append([2,rand_hexes[i],results['output'][2*i]['result'],results['output'][(2*i)+1]['result']])
					both_failures += 1

		if (verbose == 1) or (verbose == 2):
			if len(failures) == 0:
				print "******************************************************************"
				print " QIE scratch registers tested successfully (" + str(number) + " trials)"
				print "******************************************************************"
			else :
				print "*************************************************"
				print str(len(failures)) + " failures out of " + str(number) + " trials"
				print "*************************************************"
				print str(write_failures) + " write failures"
				for i in range(0,len(failures)):
					if failures[i][0] == 0:
						print "Write pattern: " + failures[i][1] + "     Write output: " + failures[i][2] + "     Read output: " + failures[i][3]
				print str(read_failures) + " read failures"
				for i in range(0,len(failures)):
					if failures[i][0] == 1:
						print "Write pattern: "+ failures[i][1] + "     Write output: " + failures[i][2] + "     Read output: " + failures[i][3]
				print str(both_failures) + " write and read failures"
				for i in range(0,len(failures)):
					if failures[i][0] == 2:
						print "Write pattern: "+ failures[i][1] + "     Write output: " + failures[i][2] + "     Read output: " + failures[i][3]
				print "*************************************************"
				total_write_failures += write_failures
				total_read_failures += read_failures
				total_both_failures += both_failures

	total_failures = total_write_failures + total_read_failures + total_both_failures
	if len(total_failures) == 0:
		print "******************************************************************"
		print " All QIE scratch registers tested successfully (" + str(number) + " trials)"
		print "******************************************************************"
		return 0
        else :
                print "*************************************************"
                print "Totals: "+ str(total_failures) + " failures out of " + str(len(slots)*number) + " trials"
                print "*************************************************"
                print str(total_write_failures) + " write failures"
                print str(total_read_failures) + " read failures"
                print str(total_both_failures) + " write and read failures"
                print "*************************************************"
		return total_failures

def QIE(number,verbose,ts):
        print "*****************************************"
        print "Testing the QIE scratch register..."
        print "*****************************************"

        random.seed()

        commands = []
        rand_ints = []
	rand_hexes = []
        for i in range(0,number):
                rand_ints.append(random.randint(10,int(0xffffffff)))
		rand_hexes.append(str(hex(rand_ints[i])))
                commands.append("put HF2-2-B_SCRATCH " + str(rand_ints[i]))
                commands.append("get HF2-2-B_SCRATCH")

        results = ngccm.send_commands_parsed( ts, commands)
        failures = []
        write_failures = 0
        read_failures = 0
        both_failures = 0	
        for i in range(0,len(results['output'])/2):
                if (results['output'][2*i]['result'] == "OK") and (results['output'][(2*i)+1]['result'] == rand_hexes[i]):
                        if verbose == 1:
                                print "Write pattern: " + rand_hexes[i] + ":     Write: Passed (" + results['output'][2*i]['result'] + ")     Read: Passed (" + results['output'][(2*i)+1]['result'] + ")"
                elif results['output'][2*i]['result'] == "OK":
                        if verbose == 1:
                                print "Write pattern: " + rand_hexes[i] + ":     Write: Passed (" + results['output'][2*i]['result'] + ")     Read: FAILED (" + results['output'][(2*i)+1]['result'] + ")"
                        failures.append([1,rand_hexes[i],results['output'][2*i]['result'],results['output'][(2*i)+1]['result']])
                        read_failures += 1
		elif results['output'][(2*i)+1]['result'] == rand_hexes[i]:
                        if verbose == 1:
                                print "Write pattern: " + rand_hexes[i] + ":     Write: FAILED (" + results['output'][2*i]['result'] + ")     Read: Passed (" + results['output'][(2*i)+1]['result'] + ")"
                        failures.append([0,rand_hexes[i],results['output'][2*i]['result'],results['output'][(2*i)+1]['result']])
                        write_failures += 1
		else:
                        if verbose == 1:
                                print "Write pattern: " + rand_hexes[i] + ":     Write: FAILED (" + results['output'][2*i]['result'] + ")     Read: FAILED (" + results['output'][(2*i)+1]['result'] + ")"
                        failures.append([2,rand_hexes[i],results['output'][2*i]['result'],results['output'][(2*i)+1]['result']])
                        both_failures += 1
	if len(failures) == 0:
		print "******************************************************************"
		print " QIE scratch register tested successfully (" + str(number) + " trials)"
		print "******************************************************************"
		return 0
        else :
                print "*************************************************"
                print str(len(failures)) + " failures out of " + str(number) + " trials"
                print "*************************************************"
                print str(write_failures) + " write failures"
                for i in range(0,len(failures)):
                        if failures[i][0] == 0:
                                print "Write pattern: " + failures[i][1] + "     Write output: " + failures[i][2] + "     Read output: " + failures[i][3]
                print str(read_failures) + " read failures"
                for i in range(0,len(failures)):
                        if failures[i][0] == 1:
                                print "Write pattern: "+ failures[i][1] + "     Write output: " + failures[i][2] + "     Read output: " + failures[i][3]
                print str(both_failures) + " write and read failures"
                for i in range(0,len(failures)):
                        if failures[i][0] == 2:
                                print "Write pattern: "+ failures[i][1] + "     Write output: " + failures[i][2] + "     Read output: " + failures[i][3]
                print "*************************************************"
		return len(failures)

def check_power(ts):
	print "**********************************"
	print "Checking backplane power status..."
	print "**********************************"

	results = ngccm.send_commands_parsed( ts, "get HF2-bkp_pwr_bad")
	if results['output'][0]['result'] == "1":
		print "************************************************"
		print "Backplane power off. Attempting to turn it on..."
		print "************************************************"
		results = ngccm.send_commands_parsed( ts, "put HF2-bkp_pwr_enable 1")
		if results['output'][0]['result'] == "OK":
			print "***************************"
			print "Power enabled. Verifying..."
			print "***************************"
			results = ngccm.send_commands_parsed( ts, "get HF2-bkp_pwr_bad")
			if results['output'][0]['result'] == "0":
				print "************************"
				print "Power verified. Proceed."
				print "************************"
				return 0
			else:
				print "************************************"
				print "Something has gone wrong. Try again."
				print "************************************"
				return 1
		else:
			print "************************************"
			print "Something has gone wrong. Try again."
			print "************************************"
			return 1
	else:
		print "************************"
		print "The power status is good"
		print "************************"
		return 0

def mezz_scratch(number,verbose,ts):
	print "*****************************************"
	print "Testing the mezzanine scratch register..."
	print "*****************************************"

	random.seed()

	commands = []
	rand_hexes = []
	rand_ints = []
	for i in range(0,number):
		rand_hex = ""
		rand_int = ""
		for j in range(0,4):
			#PATCH
			#eflag = 1
			#while eflag == 1:
			#	r = str(hex(random.randint(10,int(0xffff))))
			#	eflag = 0
			#	for letter in r:
			#		if letter == "e":
			#			eflag = 1
			#rand_hex = rand_hex + " " + r
			#/PATCH
			r = random.randint(10,int(0xffff))
			rand_int = rand_int + " " + str(r)
			rand_hex = rand_hex + " " + str(hex(r))
			#rand_hex = rand_hex + " " + str(hex(random.randint(1,int(0xffff))))
		rand_hexes.append(rand_hex.strip())
		rand_ints.append(rand_int.strip())
		commands.append("put HF2-mezz_scratch " + rand_ints[i])
		commands.append("get HF2-mezz_scratch")

	results = ngccm.send_commands_parsed( ts, commands)
	failures = []
	write_failures = 0
	read_failures = 0
	both_failures = 0
	for i in range(0,len(results['output'])/2):
		if (results['output'][2*i]['result'] == "OK") and (results['output'][(2*i)+1]['result'] == rand_hexes[i]):
			if verbose == 1:
				print "Write pattern: " + rand_hexes[i] + ":     Write: Passed (" + results['output'][2*i]['result'] + ")     Read: Passed (" + results['output'][(2*i)+1]['result'] + ")"
		elif results['output'][2*i]['result'] == "OK":
			if verbose == 1:
				print "Write pattern: " + rand_hexes[i] + ":     Write: Passed (" + results['output'][2*i]['result'] + ")     Read: FAILED (" + results['output'][(2*i)+1]['result'] + ")"
			failures.append([1,rand_hexes[i],results['output'][2*i]['result'],results['output'][(2*i)+1]['result']])
			read_failures += 1
		elif results['output'][(2*i)+1]['result'] == rand_hexes[i]:
			if verbose == 1:
				print "Write pattern: " + rand_hexes[i] + ":     Write: FAILED (" + results['output'][2*i]['result'] + ")     Read: Passed (" + results['output'][(2*i)+1]['result'] + ")"
			failures.append([0,rand_hexes[i],results['output'][2*i]['result'],results['output'][(2*i)+1]['result']])
			write_failures += 1
		else:
			if verbose == 1:
				print "Write pattern: " + rand_hexes[i] + ":     Write: FAILED (" + results['output'][2*i]['result'] + ")     Read: FAILED (" + results['output'][(2*i)+1]['result'] + ")"
			failures.append([2,rand_hexes[i],results['output'][2*i]['result'],results['output'][(2*i)+1]['result']])
			both_failures += 1
	if len(failures) == 0:
		print "******************************************************************"
		print "Mezzanine scratch register tested successfully (" + str(number) + " trials)"
		print "******************************************************************"
		return 0
	else :
		print "*************************************************"
		print str(len(failures)) + " failures out of " + str(number) + " trials"
		print "*************************************************"
		print str(write_failures) + " write failures"
		for i in range(0,len(failures)):
			if failures[i][0] == 0:
				print "Write pattern: " + failures[i][1] + "     Write output: " + failures[i][2] + "     Read output: " + failures[i][3]
		print str(read_failures) + " read failures"
		for i in range(0,len(failures)):
			if failures[i][0] == 1:
				print "Write pattern: "+ failures[i][1] + "     Write output: " + failures[i][2] + "     Read output: " + failures[i][3]
		print str(both_failures) + " write and read failures"
		for i in range(0,len(failures)):
			if failures[i][0] == 2:
				print "Write pattern: "+ failures[i][1] + "     Write output: " + failures[i][2] + "     Read output: " + failures[i][3]
		print "*************************************************"
		return len(failures)

def mezz_read(verbose,ts):
	mezz_results_file = open('mezz_results')
	mezz_results_raw = mezz_results_file.readlines()
	mezz_results_file.close()

	read_commands = []
	mezz_results = []
	for i in range(0,len(mezz_results_raw)):
		read_commands.append(mezz_results_raw[i].split(": ")[0].rstrip()) 
		mezz_results.append(mezz_results_raw[i].split(": ")[1].rstrip())

	print "******************************"
	print "Reading mezzanine registers..."
	print "******************************"

	results = ngccm.send_commands_parsed( ts, read_commands)
	error_count = 0
	problem_registers = []
	problem_expected = []
	problem_received = []
	for i in range(0,len(results['output'])):
		if results['output'][i]['result'] == mezz_results[i]:
			if verbose == 1:
				print results['output'][i]['cmd'] + ": " + results['output'][i]['result']
		else:
			if verbose == 1:
				print "ERROR on '" + results['output'][i]['cmd'] + "':     expected: " + mezz_results[i] + "     received: " + results['output'][i]['result']
			error_count += 1
			problem_registers.append(results['output'][i]['cmd'].split("et ")[1])
			problem_expected.append(mezz_results[i])
			problem_received.append(results['output'][i]['result'])

	if error_count == 0:
		print "*****************************************"
		print "All mezzanine registers read successfully"
		print "*****************************************"
		return 0
	else:
		print "*****************************************"
		print "There were " + str(error_count) + " problematic registers:"
		for i in range(0,len(problem_registers)):
			print problem_registers[i]
			print "     expected: " + problem_expected[i]
			print "     received: " + problem_received[i]
		print "*****************************************"
		return error_count
