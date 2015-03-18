from re import search
from subprocess import Popen, PIPE
import uhtr

# Functions to analyze this "data" dictionary
# Split this into check_cid_rotating(d) and check_cid_synched(d)
def check_cid(d):
	check = 1
	rotating_check = check_cid_rotating(d)
	z_rotate = rotating_check["check"]
	synched_check = check_cid_synched(d)
	z_synch = synched_check["check"]
	if (z_rotate):
		print "[O]: The CIDs are rotating correctly."
	else:
		check = 0
		print "[X]: The CIDs are NOT rotating correctly."
		print ">> The check values for each channel are {0}.".format(rotating_check["check_cid"])
	if (z_synch):
		print "[O]: The CIDs are synched across the channels."
	else:
		check = 0
		print "[X]: The CIDs are NOT synched across the channels."
		print ">> The check value for the synch is {0}.".format(z_synch)
		print ">> The error log is below:\n\n{0}".format(synched_check["log"])
		print ">> ------------------------------------------"
	return check

def check_cid_synched(d):		# Check if the CIDs are synched (equal across all channels for each BX). This function returns (1) if the CIDs are synched, (0) if they aren't, and (-1) if there is a problem with the CID data in the input.
	log = ""
	check = 0
	n_bx = 0
	n_error = 0
	try:
		n_bx = len(d["cid"])
	except Exception as ex:
		print "ERROR (check_cid_synched): Something is weird with the data. Maybe there is no data?"
		check = -1
	if (n_bx > 0):
		for j in range(n_bx):
			if ( len(set(d["cid"][j])) != 1 ):
				n_error += 1
				log += "ERROR (BX {0}): The CIDs are {1}.\n".format(j, d["cid"][j])
		if (n_error == 0 and check != -1):
			check = 1
	else:
		check = -1
	return {
			"check": check,
			"log": log,
		}

def check_cid_rotating(d):		# Check if the CIDs are rotating. This function returns (1) if the CIDs are rotating correctly, (0) if they aren't, and (-1) if there is a problem with the CID data in the input.
	log = ""
	check_cid = []
	check_total = 0
	for i in range(4):		# Loop over channels
		check = 0
		start = -1
		n_error = 0
		try:
			start = d["cid"][0][i]
		except Exception as ex:
			print "ERROR (check_cid_rotating): Something is weird with the channel {0} data. Maybe there is no data?".format(i)
		if start != -1:
			for j in range(len(d["cid"])):		# Loop over the BXs.
				if ( (j + start) % 4  != d["cid"][j][i] ):
					n_error += 1
					log += "ERROR (channel {0}): BX{1} expected CID of {2} but saw {3}.".format(i, j, (j + start) % 4, d["cid"][j][i])
		else:
			print "ERROR: The check couldn't be completed."
			check = -1
		if ( n_error == 0 and check != -1 ):
			check = 1
		check_cid.append(check)
	if (len(list(set(check_cid))) == 1):
		check_total = list(set(check_cid))[0]
	else:
		check_total = 0
	return {
		"check_cid": check_cid,
		"check": check_total,
		"log": log,
	}

if __name__ == "__main__":
	n_bx = 100
	n_samples = n_bx*4-4
	i_link = 2
#	ip_uhtr = "192.168.29.40"		# The IP address of the uHTR you want to contact (For B904)
	ip_uhtr = "192.168.100.16"		# The IP address of the uHTR you want to contact (USE THIS ONE FOR THE BHM)
	uhtr_read = uhtr.get_data(ip_uhtr, n_samples, i_link)
	data = uhtr.parse_data(uhtr_read["output"])
#	print uhtr_read["output"]
#	print data["cid"]
#	print data["adc"]
#	print data["tdc_le"]
#	print data["tdc_te"]
	print "The activated links are {0}.".format(data["links"])
	print "You're checking {0} bunch crossings. (You asked to check {1}, n_samples = {2})".format(len(data["cid"]), n_bx, n_samples)
	z_cid = check_cid(data)
	if (z_cid == 1):
		print "[O]: All checks were successful."
	else:
		print "[X]: At least one check failed!"
