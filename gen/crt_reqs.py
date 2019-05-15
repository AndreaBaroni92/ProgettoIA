# this file generates 'n' simulated requests

import glob
import sys
import os
import json
from random import randint,sample
from intent_generator import loadRequests,requestToVar
dupList = ['DPI']
def domainTodConstraints(domains_having_constraints):
	dcs = []
	counter = 0
	for d in domains_having_constraints:
		
		id_d = d + 1
		choice = randint(1,3)
		if choice == 1:
			dcs.append([id_d,'DPI',1,1])
			counter = counter +1
		elif choice == 2:
			dcs.append([id_d,'TS',1,1])
			counter = counter +1
		elif choice == 3:
			dcs.append([id_d,'DPI',1,1])
			dcs.append([id_d,'TS',1,1])
			counter = counter + 2
		if counter > len(domains_having_constraints):
			break

	# print 'receive',len(domains_having_constraints),'return',dcs
	return json.dumps(dcs)


def genReq(n_domains):
	global dupList
	# choose domains
	active_domains =  sample(range(n_domains), 2)
	start = active_domains[0] + 1 
	target = active_domains[1] + 1  

	requests = loadRequests()
	reqIdx = randint(0,len(requests)-1)
	listOfVnfString = requests[reqIdx]
	vnflist = listOfVnfString.split(',')
	p_to_s,p_to_d  = requestToVar(requests[reqIdx])
	# print p_to_d


	# domain constraints
	#domains_having_constraints =  sample(range(n_domains), n_dConstraints)
	#str_dcst,counter = domainTodConstraints(domains_having_constraints)



	out = {'src':start,'dst':target,'dupList':dupList,'vnfList':vnflist, 'prox_to_src':p_to_s,'prox_to_dst':p_to_d}


	return json.dumps(out)


def getDirPath():
	parts = os.path.abspath(__file__).split(os.sep)
	parts = parts[:-2]
	expdir = (os.sep).join(parts)
	return expdir



def call_gen_reqs(n_domains,rep,path,n_domains_constrs):


	for x in range(1,rep+1):
		outfilepath = path+str(x)+".json"
		outfilepath2 = path+"c"+str(x)+".json"

		# domain constraints
		domains_having_constraints =  sample(range(n_domains), n_domains_constrs)
		
		str_dcst= domainTodConstraints(domains_having_constraints)

		outstr = genReq(n_domains)
		with open(outfilepath, 'w+') as outfile:
			outfile.write(outstr)
		with open(outfilepath2, 'w+') as outfile2:
			outfile2.write(str_dcst)

	return path




if __name__ == '__main__':

	path = getDirPath() + os.sep+"testbed"+os.sep+"requestsJson"+os.sep

	if not os.path.exists(path):
		os.makedirs(path)



	n_domains = 8
	n_domains_constrs = 3



	path = call_gen_reqs(n_domains,10,path,n_domains_constrs)
	print ('Done, simulated user requests and constraints are generated at',path)



