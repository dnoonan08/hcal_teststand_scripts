from hcal_teststand import *
import uhtr
import ngccm
import numpy
import sys
import qie

"""
if everythings works out, you should see something like the following:
0 0FABC 03DE7 0BEEF 03DE7 0FEED 03DE7
1 0FABC 03DE8 0BEEF 03DE8 0FEED 03DE8
2 0FABC 03DE9 0BEEF 03DE9 0FEED 03DE9
3 0FABC 03DEA 0BEEF 03DEA 0FEED 03DEA
4 0FABC 03DEB 0BEEF 03DEB 0FEED 03DEB
"""

def decodeRawOutput( raw_output ) :

	raw_data = []
	output = raw_output.split("\n")
	for i in range( len( output ) ) :
		if output[i].find("N   RAW            3   2   1   0") != -1 : 
			raw_data = output[i+1:i+1801] 
			
	dataBytes = []

	for datum in raw_data :

		words = datum.split(" ")

		while "" in words :
			words.remove("")

		dataBytes.append( words[1] )

	counter= 0
	errors = 0

	for i in range( len( dataBytes ) / 6 ) :

		counter += 1

		#print i,dataBytes[i*6+0],dataBytes[i*6+1],dataBytes[i*6+2],dataBytes[i*6+3],dataBytes[i*6+4],dataBytes[i*6+5]
		if dataBytes[i*6][3:5] != "BC" :
			print "ERROR: comma character not found!",dataBytes[i*6]
			errors+=1
		#if dataBytes[i*6][1:3] != "FA" :
		#	print "ERROR: strange data found in status bits!",dataBytes[i*6][1:3]
		#	errors+=1
		if dataBytes[i*6+1] != dataBytes[i*6+3] or dataBytes[i*6+1] != dataBytes[i*6+5] or dataBytes[i*6+3] != dataBytes[i*6+5] :
			print "ERROR: at least one of the counters is inconsistent with the others!"
			print dataBytes[i*6+1]
			print dataBytes[i*6+2]
			print dataBytes[i*6+3]
			print dataBytes[i*6+4]
			print dataBytes[i*6+5]
			errors+=1
		if i > 0 :
			if int( dataBytes[i*6+1] , 16 ) - int( dataBytes[i*6-5] , 16 ) != 1 :
				print "ERROR: counter didn't increment correctly"
				errors+=1

		#print "AFTER",counter,"BXs"
		#print "ERRORS FOUND:",errors

	return errors

if __name__ == "__main__":
	name = ""
	if len(sys.argv) == 1:
		name = "bhm"
	elif len(sys.argv) == 2:
		name = sys.argv[1]
	else:
		name = "bhm"

	ts = teststand(name)

        ################
        # get uHTR link mapping 
        ################
        ngccm.link_test_modeB(ts,1,2,True)
	ngccmLog = ngccm.set_unique_id(ts,1,2)
	uhtr_map = uhtr.map_links(ts.uhtr_ips[0])
	ngccm.link_test_modeB(ts,1,2,False)


	# set unique ID on the FPGA for link mapping
	ngccm.link_test_mode(ts,1,2,True)
	# init uhtr links
	uhtr.get_links(ts.uhtr_ips[0])

        # grab data from uHTR spy function for each active link
        for link_ in uhtr_map.links :
		if not link_.on : continue
		if uhtr_map.links.index(link_) == 16 : continue
		print "==== Link {0} ====".format( uhtr_map.links.index(link_) )
		link_.Print()
		uhtr_read = uhtr.get_data(ts.uhtr_ips[0], 900 , uhtr_map.links.index(link_) )
		#print uhtr_read["output"]
		errors = decodeRawOutput( uhtr_read["output"] )
		print "ERRORS:",errors
		
	# make sure that the FPGA is in normal readout mode
	ngccm.link_test_mode(ts,1,2,False)

        
