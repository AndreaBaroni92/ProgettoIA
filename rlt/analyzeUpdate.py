import matplotlib.pyplot as plt
import os


def loadDataset(testFile):
	# print a + b
	with open(testFile, 'r') as content_file:
	    content = content_file.read()

	
	dataset = []
	pieces = content.strip().split("======")      
	pieces = [x for x in pieces if x.strip() != '']
	for piece in pieces:
		parts = piece.split("\n")
		case = parts[1]
		dic = {}
		for part in parts:
			
			if part.startswith( 'time_update:' ):
				
				runtime = part.split("time_update:")[1].strip()
				dic['time_update'] = runtime
		dataset.append([case,dic])

	return dataset


# ====================== varying nodes ======================================


domain_key = "9"
testFile = "log_n30_59_d"+domain_key+"_"+domain_key+".txt"
# testFile = "log_n30_810_d"+domain_key+"_"+domain_key+".txt"

dataset = loadDataset(testFile)
arr_str = []
arr_data = []
for nd in range(30,60):
	keycase = os.sep+"d"+domain_key+"n"+str(nd)+os.sep
	data = [entry[1] for entry in dataset if keycase in entry[0]]
	casestack = []
	for d in data:
		casestack = casestack + d['time_update'].split(",")

	casestack = [float(x) for x in casestack if x != '']
	average = sum(casestack)/len(casestack)
	arr_str.append(keycase)
	arr_data.append(average)

print (arr_str)
print (arr_data)