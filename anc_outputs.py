# Function to read the selected edit
def ReadEdit(filename):
	# Variable dictionarty
	# filename, f		: input file
	# outptut 		: an output arrays of string
	
	try:
		with open(filename, "r") as f
	except IOError as e:
		print("Couldn't open file (%s)." %e)
		return 0

