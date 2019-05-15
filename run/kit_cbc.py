'''
This script makes experiments on a set of instances,
runtime stats will be produced.
'''

import glob
import os
import time
import sys
from shutil import copyfile
import socket

def checkMZNResult(raw):
	state = "failed"
	if "=UNSATISFIABLE=" in raw or "failure" in raw:
		state = "unsat"
	elif "MIP Status: Optimal" in raw:
		state = "optsolved"
	elif "----------" in raw:
		state = "subsolved"

	return state

def getDirPath():
	parts = os.path.abspath(__file__).split("/")
	parts = parts[:-2]
	expdir = '/'.join(parts)
	return expdir


def log(testFile,out):
	with open(testFile, 'a') as outfile:
		outfile.write(out)


def run_dc(test_nodes,test_domains,test_maps,rep,solver,dc_range):

	number_of_node = str(test_nodes[0])

	dirpath = getDirPath()
	resultFolder = dirpath+"/results"
	if not os.path.exists(resultFolder):
		os.makedirs(resultFolder)
	solverfolder = resultFolder+"/"+solver
	if not os.path.exists(solverfolder):
		os.makedirs(solverfolder)

	logfile = solverfolder+"/log_n"+str(test_nodes[0])+"_"+str(test_nodes[-1])+"_d"+str(test_domains[0])+"_"+str(test_domains[-1])+".txt"


	parts = os.path.abspath(__file__).split("/")
	parts = parts[:-2]
	expdir = '/'.join(parts) + "/testbed/data-exp-n"+str(test_nodes[-1])+"-d"+str(test_domains[-1])


	# prepare log
	with open(logfile, 'w+') as outfile:
		outfile.write("")


	for domain in test_domains:

		for num_nodes in test_nodes:

			casename = "/d"+str(domain)+"n"+str(num_nodes)
			scenario = expdir+casename

			for dc in dc_range:
				for mapx in test_maps:
					solved_times = []
					subsolve_times = []
					failed_times = []
					uncompile_times = []
					unsat_times = []
					uncompile_case = []
					failed_case = []
					unsat_case = []
					subsolve_case = []
					
					mapnote = "map"+str(mapx)+".dzn"
					foldernote = "dc"+str(dc)+"/"+casename +"/"+mapnote
					testMap = scenario+"/map"+str(mapx)+".dzn"
				
					if not os.path.exists(testMap):
						sys.exit("check"+testMap)

					req_dir = scenario+"/req"+str(dc)
					for r in xrange(1,rep+1):
						testIst = req_dir+"/request"+str(r)+".dzn"
						if not os.path.exists(testIst):
							sys.exit("check"+testIst)
						parts = testIst.split("/")

						fznfile = parts[-3]+".fzn"
						fznfile = dirpath+"/tmp/"+socket.gethostname()+".fzn"
						start = time.time()

						casenote = mapnote+" "+testIst
						cmd_compile ="timeout 8 "+dirpath+ "/mzn-2.17/mzn-cbc -v -s -a -G linear "+dirpath+"/model/unique.mzn "+testMap+" "+testIst
						
						print cmd_compile
						runresult = os.popen(cmd_compile).read() 

						failed_msg = "init"
						isSuccess = False
						if runresult != "":
							# model checking failed
							failed_msg = "Notice: inconsistency "+casenote
							time_lapse = time.time()-start
	
							
							state = checkMZNResult(runresult)
							
							if state == "optsolved":
								solved_times.append(time_lapse)
								isSuccess = True
							elif state == "subsolved":
								subsolve_times.append(time_lapse)
								subsolve_case.append(casenote)
							elif state == "failed":
								failed_times.append(time_lapse)
								failed_case.append(casenote)
								failed_msg = "Notice: solving failed (crash/timeout) "+casenote
							elif state == "unsat":
								unsat_times.append(time_lapse)
								unsat_case.append(casenote)
								failed_msg = "Notice: solving unsat "+casenote
								isSuccess = False


						time_lapse = time.time()-start
						if isSuccess:
							print "Success,"
						else:
							print "Failed, ",failed_msg

						print "---"
					
					out = "======\n"+"case:"+foldernote+"\n\n"
					solved_times = [str(x) for x in solved_times]
					failed_times = [str(x) for x in failed_times]
					subsolve_times = [str(x) for x in subsolve_times]
					unsat_times = [str(x) for x in unsat_times]
					uncompile_times = [str(x) for x in uncompile_times]
					out += "optima: "+",".join(solved_times)+"\n"
					out += "suboptima: "+",".join(subsolve_times)+"\n"
					out += "unsat: "+",".join(unsat_times)+"\n"
					out += "uncompile: "+",".join(uncompile_times)+"\n"
					out += "failed: "+",".join(failed_times)+"\n\n"
					out += "---\n"
					out += "suboptimal_case:\n"+"\n".join(subsolve_case)+"\n"
					out += "failed_case:\n"+"\n".join(failed_case)+"\n"
					out += "unsat_case:\n"+"\n".join(unsat_case)+"\n"
					out += "uncompile_case:\n"+"\n".join(uncompile_case)+"\n"
					log(logfile,out)


# ==============================
# 			MAIN
# ==============================


def main(args):

	test_nodes = range(100,101)
	test_domains = range(2,31)
	test_maps = range(1,11)
	rep = 10

	filesufix = "data-exp-n"+str(test_nodes[0])
	run(test_nodes,test_domains,test_maps,rep,filesufix)

# if len(solved_times) != 0:
# 	print "avg solved time", reduce(lambda x, y: x + y, solved_times) / len(solved_times)
# if len(unsolved_times) != 0:
# 	print "avg unsolved time", reduce(lambda x, y: x + y, unsolved_times) / len(unsolved_times)