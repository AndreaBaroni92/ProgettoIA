'''
This script makes experiments on a set of instances,
runtime stats will be produced.
'''

import glob
import os
import time
import sys
import json
from util import stringification
from shutil import copyfile
from convertitore import fromReqsJsontoDzn
import socket

def updateMap(testMapJson,vnfToDelete,updateMapJson,updateMapDzn):

	change = {} # per tenere traccia dei nodi che sono stati aggiornati

	removedVnfs = [] #nodi eliminati

	removedLinks = 0 #links eliminati

	updateNodes = [] #nuova lista con i nodi usati nella soluzione eliminati

	listRemovedLinks = [] #lista archi eliminati

	updatedLinks = [] #nuova lista di archi che non contengono nodi eliminati

	if not os.path.exists(testMapJson): #controllo che esista la mappa in formato json
		sys.exit("check"+testMapJson)

	with open(testMapJson) as f:
		objMap = json.load(f)

	

	
	for a,b in enumerate(objMap["nodes"]):
		if (( vnfToDelete[a] == 1) and (b[1] != 9) and (b[1] != 10)): #vengono eliminati nodi che non siano gateway o endpoint
			removedVnfs.append(b[0])
			

	for x in objMap["nodes"]:
		if not ( x[0] in removedVnfs):
			updateNodes.append(x)


	objMap["nodes"]= updateNodes


	
	for link in objMap["node_links"]:#vengono rimossi i link che contengono almeno un nodo nei nodi eliminati
		if ((link[0] in removedVnfs) or (link[1] in removedVnfs)):
			listRemovedLinks.append(link)
			removedLinks = removedLinks + 1
	
	for link in objMap["node_links"]:#viene aggiornata lista dei links
		if not( link in listRemovedLinks ):
			updatedLinks.append(link)

	objMap["node_links"] = updatedLinks

	
	for a, b in enumerate(objMap["nodes"],1): # cambio gli indici in modo che siano sequenziali

		if (a != b[0]):
			change[b[0]] = a
			b[0]=a
	

	for link in objMap["node_links"]: #vengono aggiornati i nodi nei links
		if link[0] in change:
			link[0] = change[link[0]]
		
		if link[1] in change:
			link[1] = change[link[1]]


	objMap["n_nodes"] = objMap["n_nodes"] - len(removedVnfs) #aggiorno il numero di nodi

	objMap["num_node_links"] = objMap["num_node_links"] - removedLinks #aggiorno il numero di links


	out = stringification(objMap["n_domains"],objMap["n_nodes"],objMap["domain_link_weights"],objMap["node_links"],objMap["nodes"],objMap["M"],objMap["num_node_links"])

	if (os.path.dirname(updateMapJson)):
		os.makedirs(os.path.dirname(updateMapJson), exist_ok=True)

	with open(updateMapJson, 'w+') as outfile:
		outfile.write(json.dumps(objMap))

	with open(updateMapDzn, 'w+') as outfile1:
		outfile1.write(out)


def checkMZNResult(raw):
	state = "failed"
	if "=UNSATISFIABLE=" in raw or "failure" in raw:
		state = "unsat"
	elif "==========" in raw:
		state = "optsolved"
	elif "----------" in raw:
		state = "subsolved"

	return state


def log(testFile,out):
	with open(testFile, 'a') as outfile:
		outfile.write(out)

def getDirPath():
	parts = os.path.abspath(__file__).split(os.sep)
	parts = parts[:-2]
	expdir = (os.sep).join(parts)
	return expdir

def run_dc(test_nodes,test_domains,test_maps,rep,solver,dc_range):

	number_of_node = str(test_nodes[0])

	
	# resultFolder = "results-c"
	dirpath = getDirPath()
	resultFolder = dirpath+os.sep+"results2"
	if not os.path.exists(resultFolder):
		os.makedirs(resultFolder)
	solverfolder = resultFolder+os.sep+solver
	if not os.path.exists(solverfolder):
		os.makedirs(solverfolder)

	logfile = solverfolder+os.sep+"log_n"+str(test_nodes[0])+"_"+str(test_nodes[-1])+"_d"+str(test_domains[0])+"_"+str(test_domains[-1])+".txt"



	parts = os.path.abspath(__file__).split(os.sep)
	parts = parts[:-2]
	expdir = (os.sep).join(parts) + os.sep+"testbed"+os.sep+"data-exp-n"+str(test_nodes[-1])+"-d"+str(test_domains[-1])

	print("directory : "+ expdir)

	# prepare log
	with open(logfile, 'w+') as outfile:
		outfile.write("")


	for domain in test_domains:

		for num_nodes in test_nodes:

			casename = os.sep+"d"+str(domain)+"n"+str(num_nodes)
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
					foldernote = "dc"+str(dc)+os.sep+casename +os.sep+mapnote
					testMap = scenario+os.sep+"map"+str(mapx)+".dzn"
					testMapJson = scenario+os.sep+"map"+str(mapx)+".json"
				
					if not os.path.exists(testMap):
						sys.exit("check"+testMap)

					if not os.path.exists(testMapJson):
						sys.exit("check"+testMapJson)

					req_dir = scenario+os.sep+"req"+str(dc)
					for r in range(1,rep+1):


						userReq = req_dir+os.sep+"r"+str(r)+".json"

						if not os.path.exists(userReq):
							sys.exit("check"+userReq)
                        #devo ricontrollare se la mappa esiste perche' puo' essere stata aggiornata rimuovendo i vnf non utilizzati
						if not os.path.exists(testMap):
							sys.exit("check"+testMap)
                        #viene controllata anche la mappa in formato json
						if not os.path.exists(testMapJson):
							sys.exit("check"+testMapJson)

						domCons = req_dir+os.sep+"rc"+str(r)+".json"

						if not os.path.exists(domCons):
							sys.exit("check"+domCons)
						#parts = testIst.split(os.sep)

						testIst = req_dir+os.sep+"request"+str(r)+".dzn"

						fromReqsJsontoDzn(userReq,domCons,testIst)

						if not os.path.exists(testIst):
							sys.exit("check"+testIst)
						parts = testIst.split(os.sep)

		
						fznfile = dirpath+os.sep+"tmp"+os.sep+socket.gethostname()+".fzn"
						
						#creo la directory dove e' contenuto fznfile
						if (os.path.dirname(fznfile)):
							os.makedirs(os.path.dirname(fznfile), exist_ok=True)


						start = time.time()

						casenote = mapnote+" "+testIst


						timeoutcmd = ""
						# print socket.gethostname()
						# sys.exit()
						if "nt" not in os.name:
								timeoutcmd = "timeout 6 "

						
						cmd_compile =timeoutcmd + "mzn2fzn -c  --time-limit 12000 "+dirpath+os.sep+"model"+os.sep+"model.mzn "+testMap+" "+testIst+" -o "+fznfile
						
						print (cmd_compile)

						compileinfo = os.popen(cmd_compile).read()

						
						
						isSuccess = True
						if compileinfo != "":
							# model checking failed
							failed_msg = "Notice: inconsistency "+casenote
							time_lapse = time.time()-start
							uncompile_times.append(time_lapse)
							uncompile_case.append(casenote)
							isSuccess = False
							
							# continue
						
						# if timeout
						time_lapse_test = time.time()-start
						if time_lapse_test > 11:
							failed_msg = "compile timeout "+casenote
							failed_times.append(time_lapse_test)
							failed_case.append(casenote)
							isSuccess = False

						if isSuccess:
							if "nt" in os.name:
								cmd = "."+os.sep+"fzn-chuffed.exe -t 12000 "+fznfile
							elif solver == "ortools":
								cmd = "timeout 5 "+dirpath+os.sep+"or-tools_v6.7"+os.sep+"bin"+os.sep+"fzn-or-tools "+fznfile
							elif solver == "gecode":
								cmd = "timeout 5 "+dirpath+os.sep+"mzn-2.17"+os.sep+"fzn-gecode "+fznfile
							elif solver == "choco":
								cmd = "timeout 5 java -jar "+dirpath+os.sep+"choco"+os.sep+"choco-parsers-3.3.0-with-dependencies.jar "+fznfile
							elif solver == "jacop":
								cmd = "timeout 5 java -jar "+dirpath+os.sep+"jacop"+os.sep+"jacop-4.5.0-SNAPSHOT.jar "+fznfile
							
							else:
								cmd = "timeout 5 "+dirpath+os.sep+"fzn_chuffed "+fznfile
							
							rlt = os.popen(cmd).read() # This will run the command and return any output
							

							time_lapse = time.time()-start
							state = checkMZNResult(rlt)#identificare  i nodi eventualmente usati nella soluzione
							
							if state == "optsolved":
								solved_times.append(time_lapse)
								#print(rlt)

								# toparse= rlt.splitlines()

								# print("www "+str(len(toparse)))
								lToParse= rlt.replace('\n', '').replace('\r', '').strip().split(';')
								lToParsenoWs = [x.strip() for x in lToParse]
								vnfToDelete = []
								for s in lToParsenoWs:
									if s.startswith('selected_nodes'):
										startsb=s.find('[') +1
										endsb=s.find(']')
										vnfToDelete = s[startsb:endsb].split(',')
										break				
										#print(len(ris))
								# print(rlt)
								
								vnfToDeleteInt = [int(x) for x in vnfToDelete]
								
								updateMapJson = scenario+os.sep+"map"+str(mapx)+"req"+str(dc)+"request"+str(r)+".json"
								updateMapDzn = scenario+os.sep+"map"+str(mapx)+"req"+str(dc)+"request"+str(r)+".dzn"
								
								updateMap(testMapJson,vnfToDeleteInt,updateMapJson,updateMapDzn)	
								testMapJson = updateMapJson
								testMap = updateMapDzn



							elif state == "subsolved":
								subsolve_times.append(time_lapse)
								subsolve_case.append(casenote)
							elif state == "failed":
								failed_times.append(time_lapse)
								failed_case.append(casenote)
								failed_msg = "Notice: solving failed (crash"+os.sep+"timeout) "+casenote

								isSuccess = False
							elif state == "unsat":
								unsat_times.append(time_lapse)
								unsat_case.append(casenote)
								failed_msg = "Notice: solving unsat "+casenote
								isSuccess = False


						
						if isSuccess:
							print ("Success,")
						else:
							print ("Failed, ",failed_msg)

						print ("---")
					
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
#aggiornare la mappa togliendo i nodi e gli archi tranne gateway e endpoint

# def run(test_nodes,test_domains,test_maps,rep,filesufix,solver):

# 	number_of_node = str(test_nodes[0])

	
# 	resultFolder = "results"
# 	if not os.path.exists(resultFolder):
# 		os.makedirs(resultFolder)
# 	solverfolder = resultFolder+os.sep+solver
# 	if not os.path.exists(solverfolder):
# 		os.makedirs(solverfolder)

# 	logfile = solverfolder+os.sep+"log_n"+str(test_nodes[0])+"_"+str(test_nodes[-1])+"_d"+str(test_domains[0])+"_"+str(test_domains[-1])+".txt"


# 	parts = os.path.abspath(__file__).split(os.sep)
# 	parts = parts[:-1]
# 	# expdir = (os.sep).join(parts) + os.sep+"data-exp-n"+number_of_node
# 	expdir = (os.sep).join(parts) + os.sep+filesufix

# 	# prepare log
# 	with open(logfile, 'w+') as outfile:
# 		outfile.write("")


# 	for domain in test_domains:

# 		for num_nodes in test_nodes:

# 			casename = os.sep+"d"+str(domain)+"n"+str(num_nodes)
# 			scenario = expdir+casename

# 			for mapx in test_maps:
# 				solved_times = []
# 				subsolve_times = []
# 				failed_times = []
# 				uncompile_times = []
# 				unsat_times = []
# 				uncompile_case = []
# 				failed_case = []
# 				unsat_case = []
# 				subsolve_case = []
				
# 				mapnote = "map"+str(mapx)+".dzn"
# 				foldernote = casename +os.sep+mapnote
# 				testMap = scenario+os.sep+"map"+str(mapx)+".dzn"
			
# 				if not os.path.exists(testMap):
# 					sys.exit("check"+testMap)

# 				req_dir = scenario+os.sep+"req"
# 				for r in xrange(1,rep+1):
# 					testIst = req_dir+os.sep+"request"+str(r)+".dzn"
# 					if not os.path.exists(testIst):
# 						sys.exit("check"+testIst)
# 					parts = testIst.split(os.sep)

# 					fznfile = parts[-3]+".fzn"
# 					fznfile = "tmp"+os.sep+""+socket.gethostname()+".fzn"
# 					# print fznfile 
# 					# print socket.gethostname()
# 					# sys.exit() 
					
# 					start = time.time()

# 					casenote = mapnote+" "+testIst


# 					timeoutcmd = ""
# 					if "Tongs-MacBook-Air" not in socket.gethostname():
# 							timeoutcmd = "timeout 6 "

# 					cmd_compile =timeoutcmd + "mzn2fzn -I mznlib model"+os.sep+"unique.mzn "+testMap+" "+testIst+" -o "+fznfile
# 					print cmd_compile
# 					compileinfo = os.popen(cmd_compile).read() 

# 					isSuccess = True
# 					if compileinfo != "":
# 						# model checking failed
# 						failed_msg = "Notice: inconsistency "+casenote
# 						time_lapse = time.time()-start
# 						uncompile_times.append(time_lapse)
# 						uncompile_case.append(casenote)
# 						isSuccess = False
# 						# continue
					
# 					# if timeout
# 					time_lapse_test = time.time()-start
# 					if time_lapse_test > 5:
# 						failed_msg = "compile timeout "+casenote
# 						failed_times.append(time_lapse_test)
# 						failed_case.append(casenote)
# 						isSuccess = False

# 					if isSuccess:
# 						if "Tongs-MacBook-Air" in socket.gethostname():
# 							cmd = "."+os.sep+"fzn_chuffed.dms "+fznfile
# 						elif solver == "ortools":
# 							cmd = "timeout 5 or-tools_v6.7"+os.sep+"bin"+os.sep+"fzn-or-tools "+fznfile
# 						elif solver == "gecode":
# 							cmd = "timeout 5 mzn-2.17"+os.sep+"fzn-gecode "+fznfile
# 						else:
# 							cmd = "timeout 5 ."+os.sep+"fzn_chuffed "+fznfile
						
# 						rlt = os.popen(cmd).read() # This will run the command and return any output
						
# 						time_lapse = time.time()-start
# 						state = checkMZNResult(rlt)
						
# 						if state == "optsolved":
# 							solved_times.append(time_lapse)
# 						elif state == "subsolved":
# 							subsolve_times.append(time_lapse)
# 							subsolve_case.append(casenote)
# 						elif state == "failed":
# 							failed_times.append(time_lapse)
# 							failed_case.append(casenote)
# 							failed_msg = "Notice: solving failed (crash"+os.sep+"timeout) "+casenote

# 							#test 
# 							# print failed_msg
# 							# sys.exit()


# 							isSuccess = False
# 						elif state == "unsat":
# 							unsat_times.append(time_lapse)
# 							unsat_case.append(casenote)
# 							failed_msg = "Notice: solving unsat "+casenote
# 							isSuccess = False


					
# 					if isSuccess:
# 						print "Success,"
# 					else:
# 						print "Failed, ",failed_msg

# 					print "---"
				
# 				out = "======\n"+"case:"+foldernote+"\n\n"
# 				solved_times = [str(x) for x in solved_times]
# 				failed_times = [str(x) for x in failed_times]
# 				subsolve_times = [str(x) for x in subsolve_times]
# 				unsat_times = [str(x) for x in unsat_times]
# 				uncompile_times = [str(x) for x in uncompile_times]
# 				out += "optima: "+",".join(solved_times)+"\n"
# 				out += "suboptima: "+",".join(subsolve_times)+"\n"
# 				out += "unsat: "+",".join(unsat_times)+"\n"
# 				out += "uncompile: "+",".join(uncompile_times)+"\n"
# 				out += "failed: "+",".join(failed_times)+"\n\n"
# 				out += "---\n"
# 				out += "suboptimal_case:\n"+"\n".join(subsolve_case)+"\n"
# 				out += "failed_case:\n"+"\n".join(failed_case)+"\n"
# 				out += "unsat_case:\n"+"\n".join(unsat_case)+"\n"
# 				out += "uncompile_case:\n"+"\n".join(uncompile_case)+"\n"
# 				log(logfile,out)


# ==============================
# 			MAIN
# ==============================


def main(args):

	test_nodes = range(100,101)
	test_domains = range(2,31)
	test_maps = range(1,11)
	rep = 10

	filesufix = "data-exp-n"+str(test_nodes[0])
	#run(test_nodes,test_domains,test_maps,rep,filesufix) ( ho cancellato perche' penso non venga usato)

# if len(solved_times) != 0:
# 	print "avg solved time", reduce(lambda x, y: x + y, solved_times) "+os.sep+" len(solved_times)
# if len(unsolved_times) != 0:
# 	print "avg unsolved time", reduce(lambda x, y: x + y, unsolved_times) "+os.sep+" len(unsolved_times)