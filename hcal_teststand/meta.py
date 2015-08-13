# FUNCTIONS:

# Parse common teststand arguments:
## Parse crate, slot arguments to construct something in the form of ts.fe:
def parse_args_crate_slot(ts=None, crate=None, slot=None, crate_type="fe"):
	if crate_type == "utca":
		crate_type = "be"
	if not (crate_type == "fe" or crate_type == "be"):
		print "ERROR (meta.parse_crate_slot_args): The \"crate_type\" of {0} wasn't recognized. It should be \"fe\" for front-end or \"be\" for back-end.".format(crate_type)
		return False
	
	if ts:
		assessment = sum([
			(isinstance(crate, int) or isinstance(crate, list)) and crate != None,
			(isinstance(slot, int) or isinstance(slot, list)) and slot != None,
		])
		
		# If both crate and slot are defined correctly:
		if assessment == 2:
			# Turn things into lists:
			if isinstance(crate, int):
				crates = [int(crate)]
			elif isinstance(crate, list):
				crates = crate
			if isinstance(slot, int):
				slots = [int(slot)]
			elif isinstance(slot, list):
				slots = slot
			
			# Allow things like crate = 1 (-> [1]) and slot = [2, 3] (will be turned into [[2, 3]]:
			if len(crates) == 1:
				if not isinstance(slots[0], list):
					slots = [slots]
				elif len(slots) > 1:	# Disallow slot = [[2], [3]]
					print "ERROR (meta.parse_crate_slot_args): The crate/slot configuration is too confusing."
					return False
			
			# Deal with more standard expected notaion:
			else:
				if not isinstance(slots[0], list):
					print "ERROR (meta.parse_crate_slot_args): The crate/slot configuration is too confusing."
					return False
				else:
					if len(crates) != len(slots):
						print "ERROR (meta.parse_crate_slot_args): The crate/slot configuration is too confusing."
						return False
			
			# Finally, return the crate, slot configuration:
			crate_info = {}
			for i, c in enumerate(crates):
				crate_info[c] = slots[i]
			return crate_info
		
		# If either crate or slot is defined correctly:
		elif assessment == 1:
			if crate != None and slot == None:
				# Turn things into lists:
				if isinstance(crate, int):
					crates = [int(crate)]
				elif isinstance(crate, list):
					crates = crate
				
				# Asign the default slots from the teststand object:
				crate_info = {}
				for i in crates:
					if i in getattr(ts, crate_type):
						crate_info[i] = getattr(ts, crate_type)[i]
					else:
						crate_info[i] = []
				return crate_info
			else:
				print "ERROR (meta.parse_crate_slot_args): You entered slot = {0}, but crate = {1}. What did you expect to happen?".format(slot, crate)
				return False
		
		# If neither crate nor slot is defined correctly:
		elif assessment == 0:
			if crate == None and slot == None:
				return getattr(ts, crate_type)
			else:
				print "ERROR (meta.parse_crate_slot_args): The crate and slot arguments must either be integers or lists. You entered the following:"
				print "\tcrate = {0}\n\tslot={1}".format(crate, slot)
				return False
	else:
		print "ERROR (meta.parse_crate_slot_args): You must supply a teststand argument!"
		return False
## /

## Parse i_qie:
def parse_args_qie(i_qie=None):
	if i_qie != None:
		i_qie_original = i_qie
		if isinstance(i_qie, int):
			i_qie = [int(i_qie)]
		if not isinstance(i_qie, list):
			print "ERROR (meta.parse_args_qie): You must enter an integer or a list of integers for \"i_qie\"."
			return False
		else:
			i_qie = set(i_qie)
			if not i_qie.issubset(set(range(1, 25))):
				print "ERROR (meta.parse_args_qie): \"i_qie\" can only contain elements of [1, 2, ..., 24], but you tried to set it to {0}.".format(i_qie_original)
				return False
			else:
				return sorted(list(i_qie))
	else:
		return range(1, 25)
## /
# /

# /FUNCTIONS
