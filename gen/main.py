import xml.etree.ElementTree as ET
import sys,os
from os import listdir
from os.path import isfile, join
from gen_map import filterNode,getNumberOfDomains,ns,getAtrId,generateMap
from crt_reqs import call_gen_reqs
def getNumbDom(inp):
        tree = ET.parse(inp)
        root = tree.getroot()
	# ----------------------------
        
        idLat = getAtrId(root.findall('.//n:key',ns),'latitude')
        idLon = getAtrId(root.findall('.//n:key',ns),'longitude')

        if (idLat == "non trovato" or idLon == "non trovato" ):
                print("Non è possibile recuperare la latitudine e la longitudine nel file")
                sys.exit(1)

        listOfNodes = root.findall('.//n:graph/n:node[@id]',ns)

        listOfNodes = filterNode(listOfNodes, idLat,idLon)# restituisce una lista di nodi che hanno latitudine e longitudine

        numbOfDomains = getNumberOfDomains(listOfNodes) #numero di domini

        return numbOfDomains

def exc(inp,test_nodes,test_domains,test_maps,test_dcons,expdir,rep):
        for i,domain in enumerate(test_domains):
                for num_nodes in test_nodes:
                        scenario = expdir+os.sep+"d"+str(domain)+"n"+str(num_nodes)
                        if not os.path.exists(scenario):
                                os.makedirs(scenario)

                        for mapx in test_maps:
                                filepath = scenario+os.sep+"map"+str(mapx)+".dzn"
                                generateMap(inp[i],filepath,num_nodes)
                                
                        for dc in test_dcons:
                                
                                req_dir = scenario + os.sep+"req"+str(dc)
                                if not os.path.exists(req_dir):
                                        os.makedirs(req_dir)

                                req_path = req_dir+os.sep+"r"
                                call_gen_reqs( domain,rep,req_path,dc)




def test():
        test_nodes = range(30,60)

        listOfMap = []

        test_domains = []
        test_dcons = [1]
        
        #test_dcons = range(2,3)

        test_maps = range(1,2)


        
        for file in os.listdir("Map"):#legge le mappe dentro la cartella Map
                if file.endswith(".graphml"):
                        listOfMap.append(os.path.join("Map", file))
        
        for i in listOfMap:#recupera il numero di domini delle mappe all'interno della cartella Map
                test_domains.append(getNumbDom(i))

        test_domains.sort()
        parts = os.path.abspath(__file__).split(os.sep)
        parts = parts[:-2]
        expdir = os.sep.join(parts) + os.sep+"testbed"+os.sep+"data-exp-n"+str(test_nodes[-1])+"-d"+str(test_domains[-1])
	# expdir = '/'.join(parts) + "/data-exp-n"+str(test_nodes[-1])+"-d"+str(test_domains[-1])

        rep = 10




        exc(listOfMap,test_nodes,test_domains,test_maps,test_dcons,expdir,rep)


test()


