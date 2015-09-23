####################################################################
# Type: MODULE                                                     #
#                                                                  #
# Description: [description]                                       #
####################################################################

# IMPORTS:
# /IMPORTS

# VARIABLES:
# /VARIABLES

# CLASSES:
# /CLASSES

# FUNCTIONS:
def single_card(qid="0x67000000 0x9B32C370", be_crate=53, be_slot=1, fe_crate=2, fe_slot=2, link=18):
	qie_map = []
	for i_qie in range(1, 25):
		i_link = link + (i_qie - 1)/4
		ch = (i_qie - 1)%4
		half = (24 - i_qie)/12
		fiber = ((i_qie - 1)/4)%3
		qie_map.append({
			"be_crate": be_crate,
			"be_slot": be_slot,
			"fe_crate": fe_crate,
			"fe_slot": fe_slot,
			"qie_n": i_qie,
			"qie_id": qid,
			"uhtr_link": i_link,
			"uhtr_channel": ch,
			"uhtr_half": half,
			"uhtr_fiber": fiber,
		})
	return qie_map
# /FUNCTIONS
