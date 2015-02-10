import os, re
n_bx = 7
n_samples = n_bx*4-4
n_channel = 14
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
print "---"
print uhtr_script
print "---"
#raw_output = "{0}\n{1}".format("=========", os.popen("uHTRtool.exe 192.168.29.40 -s qie_card_valid.txt").read())
raw_output = open("qie_card_valid_out.txt").read()
with open("qie_card_valid_out.txt", "w") as out:
	out.write(raw_output)
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
		data["cid"].append(line.split()[-4:])
        adc_match = re.search("ADCs", line)
        if adc_match:
                data["adc"].append(line.split()[-4:])
        tdc_le_match = re.search("LE-TDC", line)
        if tdc_le_match:
                data["tdc_le"].append(line.split()[-4:])
        tdc_te_match = re.search("TE-TDC", line)
        if tdc_te_match:
                data["tdc_te"].append(line.split()[-4:])

print raw_data
print len(raw_data)
print data["cid"]
print data["adc"]
print data["tdc_le"]
print data["tdc_te"]
