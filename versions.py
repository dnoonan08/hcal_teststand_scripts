from re import search
from subprocess import Popen, PIPE

def get_amc_info():
	raw_output = Popen(['printf "fv\nq" | AMC13Tool2.exe -c ~elaird/AMC13_sn54.xml'], shell = True, stdout = PIPE, stderr = PIPE)
	version = 0
	log = ""
	try:
		match = search("^Using AMC13 software ver:(\d+)", raw_output.communicate()[1].strip())		# communicate()[1] contains the stderr. For some reason the verion number is printed on stderr...
		version = match.group(1)
	except Exception as ex:
		log += "Trying to find AMC13 version number resulted in: {0}\n".format(ex)
	return {
		"version":	version,
		"log":		log,
	}

if __name__ == "__main__":
	amc_info = get_amc_info()
#	print amc_info
	print amc_info["version"]
	print amc_info["log"]
