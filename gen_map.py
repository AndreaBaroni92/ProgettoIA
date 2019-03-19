import xml.etree.ElementTree as ET
import sys, getopt , os
from operator import itemgetter
from geopy.distance import lonlat, distance
ns = {'n':'http://graphml.graphdrawing.org/xmlns'} #namespace
# VNF attribute KEYs
VNF_KEY_ID = 0
VNF_KEY_TYPE = 1


# VNF type IDs
GATEWAY = 9
ENDPOINT = 10
WANA = 2
DPI = 1
SHAPER = 3
VPN = 4
NAT = 5
type_list = [DPI,WANA,SHAPER,VPN,NAT]


def initVNFs(vnf_ids):
	vnfs = []
	for idx in vnf_ids:
		vnfs.append([idx+1,0, 0, 0, 0, 0, 1, 0])
	return vnfs

def getNumberOfDomains(root): #restituisce il numero di nodi univoci
        listOfN=[] #per avere una lista univoca
        for n in root:
                if not(n.get('id')) in listOfN:
                        listOfN.append(n.get('id'))
        return len(listOfN)

def createNodeLinks(listOfNodes): #costruisce la lista di links 
        links = []
        for n in listOfNodes:
                s = int(n.get('source'))
                t = int(n.get('target'))
                if not ([s,t] in links):
                        links.append([s,t])
        return links
        

def getSourceFile(argv):
        if len(sys.argv) <= 1:
                print('gen_map.py -i <inputfile>')
                exit(1)
        try:
             opts ,args= getopt.getopt(argv,"hi:",["ifile="])
        except getopt.GetoptError:
                print ('gen_map.py -i <inputfile>')
                sys.exit(2)
        for opt, arg in opts:
                if opt == '-h':
                        print ('gen_map.py -i <inputfile>')
                        sys.exit()
                elif opt in ("-i", "--ifile"):
                        inputfile = arg
                        if not (os.path.isfile(inputfile)):
                                print("file "+ inputfile+ " doesn't exist")

        return inputfile

def getAtrId(InputNodes,s): #funzione per recuperare id dato atr.name
        ris="non trovato"
        for n in InputNodes:
                if n.get('attr.name').replace(" ","").lower() == s:
                        ris = n.get("id")
        return ris


def getDistance(a,b):#calcola la distanza tra due punti a e b che rappresentano ciascuno la latitudine e la longitudine
        return int(distance(lonlat(*a), lonlat(*b)).km)

def getInfo(id,listOfNodes,InfoId): #restituisce la latitudine o longitudine di un nodo identificato da un id presente nella lista dei nodi
        ris = 0
        for n in listOfNodes:             
                if n.get('id') == str(id):                       
                        for child in n.iter('{http://graphml.graphdrawing.org/xmlns}data'):                               
                                if child.get('key') == InfoId:
                                        ris = child.text
        return ris
                        

def setDomainsCost(domainsCosts,domainsLinks,listOfNodes,idLat,idLon):
        for i in range(len(domainsCosts)):
                for j in range(len(domainsCosts)):
                        if [i,j] in domainsLinks:
                                x = getInfo(i,listOfNodes,idLon)
                                y = getInfo(i,listOfNodes,idLat)
                                z = getInfo(j,listOfNodes,idLon)
                                w = getInfo(j,listOfNodes,idLat)
                                ris = getDistance((x,y),(z,w))
                                domainsCosts[i][j]= ris

        

#MAIN       

if __name__ == "__main__":
        
        inp =  getSourceFile(sys.argv[1:])
        tree = ET.parse(inp)
        root = tree.getroot()
	# ----------------------------
        '''str_vnf_link = "[|"
        for i in range(len(listOfNodeLinks)):
                str_vnf_link += str(listOfNodeLinks[i][0])+","+str(listOfNodeLinks[i][1]) + "|"

        str_vnf_link = str_vnf_link[:-1]
        str_vnf_link += "|"
        str_vnf_link += "]"

        out =  "n_domains = "+str(numbOfDomains)+";\n"
        out += "num_node_links = "+str(len(listOfNodeLinks))+";\n"
        out += "node_links = "+str_vnf_link+";\n"
  
        filepath = 'exampleMap.dzn'

        with open(filepath, 'w+') as outfile:
                outfile.write(out)'''
        
        idLat = getAtrId(root.findall('.//n:key',ns),'latitude')
        idLon = getAtrId(root.findall('.//n:key',ns),'longitude')
        listOfNodes = root.findall('.//n:graph/n:node[@id]',ns)
        numbOfDomains = getNumberOfDomains(listOfNodes) #numero di domini
        domainsCosts = [[0 for x in range(numbOfDomains)] for y in range(numbOfDomains)] #lista per memorizzare il costo fra i vari domini inizializzata a zero

        #print(domainsCosts)
        listOfNodeLinks = createNodeLinks(root.findall('.//n:graph/n:edge[@source][@target]',ns))
        listOfNodeLinks.sort(key=lambda elem: elem[0])
        setDomainsCost(domainsCosts,listOfNodeLinks,listOfNodes,idLat,idLon) #genera la distanza fra i vari domini
        print(domainsCosts)
        

        #crea info riguardo ai nodi