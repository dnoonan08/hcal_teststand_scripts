import os, re

# Configuration things
n_bx = 7
n_samples = n_bx*4-4
n_channel = 14

# Read data from the uHTR
uhtr_script = '''## BEGIN uhtr script ##
0
link
init
1
92
status
spy
{0}
0
0
{1}
quit
exit
exit
## END uhtr script ##'''.format(n_channel, n_samples)
with open("qie_card_valid.txt", "w") as out:
	out.write(uhtr_script)
#print "---"
#print uhtr_script
#print "---"
raw_output = "{0}\n{1}".format("=========", os.popen("uHTRtool.exe 192.168.29.40 -s qie_card_valid.txt").read())
#raw_output = open("qie_card_valid_out.txt").read()
with open("qie_card_valid_out.txt", "w") as out:
	out.write(raw_output)

# Some functions that parse "raw_output"
def active_channels(raw):		# Produces a list of activated channels
	active = []
	n_times = 0
	for line in raw.split("\n"):
		if re.search("^Status\s*\|", line):
			n_times += 1
			statuses = line.split("|")
			for i in range(len(statuses)):
				if statuses[i].strip() == "ON":
					active.append(i - 1)
	if n_times < 1:
		print ">> ERROR: No \"init\" was called on the link."
	if n_times > 1:
		print ">> ERROR: Hm, \"init\" was called on the link multiple times, so the active channel list might be unreliable."
	return active


# Parse uHTR data
n = 0
raw_data = []
for line in raw_output.split("\n"):
	if re.search("\s*\d+\s*[0123456789ABCDEF]{5}", line):
		raw_data.append(line.strip())
data = {
	"cid": [],
	"adc": [],
	"tdc_le": [],
	"tdc_te": [],
}
for line in raw_data:
	cid_match = re.search("CAPIDS", line)
	if cid_match:
		data["cid"].append([int(i) for i in line.split()[-4:]])
	adc_match = re.search("ADCs", line)
	if adc_match:
		data["adc"].append([int(i) for i in line.split()[-4:]])
	tdc_le_match = re.search("LE-TDC", line)
	if tdc_le_match:
		data["tdc_le"].append([int(i) for i in line.split()[-4:]])
	tdc_te_match = re.search("TE-TDC", line)
	if tdc_te_match:
		data["tdc_te"].append([int(i) for i in line.split()[-4:]])
data["channels"] = active_channels(raw_output)

# Functions to analyze this "data" dictionary
def check_cid(d):		# Check if the CIDs are rotating.
	start = -1
	n_error = 0
	if ( len(set(d["cid"][0])) == 1 ):		# Check that all CIDs start at the same value.
		start = list(set(d["cid"][0]))[0]
	if start != -1:
#		print start
		for i in range(4):		# Loop over each channel.
			for j in range(len(d["cid"])):		# Loop over the BXs.
				if ( (j + start) % 4  != d["cid"][j][i] ):
					n_error += 1
#					print j
#					print d["cid"][j]
	else:
		">> ERROR: The CIDs don't all start at the same value!"
	check = 0
	if ( n_error == 0 ):
		check = 1
	return check

#print raw_data
#print len(raw_data)
#print data["cid"]
#print data["adc"]
#print data["tdc_le"]
#print data["tdc_te"]
channels = active_channels(raw_output)
print ">> The activated channels are {0}.".format(channels)
print ">> You're checking {0} bunch crossings.".format(len(data["cid"]))
z_cid = check_cid(data)
if z_cid:
	print ">> The CIDs are rotating correctly."
else:
	print ">> DANGER: The CIDs are not rotating correctly."
