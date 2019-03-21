import xml.etree.ElementTree as ET
import sys, getopt , os
import random
from operator import itemgetter
from geopy.distance import lonlat, distance
ns = {'n':'http://graphml.graphdrawing.org/xmlns'} #namespace
# VNF attribute KEYs
VNF_KEY_ID = 0
VNF_KEY_TYPE = 1
VNF_KEY_DOMAIN = 7

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

def maxM(l): #massimo costo da dominio a dominio
        flat_list = [item for sublist in l for item in sublist]
        return max(flat_list)

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
        inputfile = ''
        outputfile = ''
        if len(sys.argv) <= 4:
                print('gen_map.py -i <inputfile> -o <outputfile>')
                sys.exit(1)
        try:
             opts ,args= getopt.getopt(argv,"hi:o:",["ifile=","ofile=" ])
        except getopt.GetoptError:
                print ('gen_map.py -i <inputfile> -o <outputfile>  ')
                sys.exit(2)
        for opt, arg in opts:
                if opt == '-h':
                        print ('gen_map.py -i <inputfile>')
                        sys.exit()
                elif opt in ("-i", "--ifile"):
                        inputfile = arg
                        if not (os.path.isfile(inputfile)):
                                print("file "+ inputfile+ " doesn't exist")
                                sys.exit(1)
                elif opt in ("-o", "--ofile"):
                        outputfile = arg

        return inputfile , outputfile

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





def createVNFLinks(domains_links,vnfs):
        global VNF_KEY_TYPE, GATEWAY,VNF_KEY_DOMAIN

        vnf_links = []
        vnf_links.extend(domains_links)

        #all' interno di uno stesso dominio detto b il nodo GATEWAY e a un nodo di tipo non GATEWAY
        # esiste un arco (a,b) e un arco ( b,a)

        for i in [idx for idx, vnf in enumerate(vnfs) if vnf[VNF_KEY_TYPE] == GATEWAY]:
                for j in [idx for idx, vnf in enumerate(vnfs) if vnf[VNF_KEY_TYPE] != GATEWAY and  vnf[VNF_KEY_DOMAIN] == vnfs[i][VNF_KEY_DOMAIN] ]:
                        vnf_links.append([vnfs[i][0],vnfs[j][0]])
                        vnf_links.append([vnfs[j][0],vnfs[i][0]])

        return vnf_links


def call_gen_map(n_domains,n_vnfs,domains_links,domainsCosts,filepath):
        global VNF_KEY_TYPE,VNF_KEY_DOMAIN,GATEWAY,ENDPOINT,WANA,SHAPER,DPI,type_list

        vnf_ids = list(range(n_vnfs))
        domain_ids = range(1,n_domains+1)
        vnfs = initVNFs(vnf_ids)

        # i nodi da 0 a n_domains -1 sono di tipo GATEWAY (per ogni dominio deve esserci almeno un GATEWAY)

        for d in range(n_domains): 
                tmpid = vnf_ids[0]
                vnfs[tmpid][VNF_KEY_TYPE] = GATEWAY
                vnfs[tmpid][VNF_KEY_DOMAIN] = d+1
                del vnf_ids[0]
        
        # i nodi da n_domains  a  2*n_domains -1  sono di tipo ENDPOINT (per ogni dominio deve esserci almeno un ENDPOINT)

        for d in range(n_domains): 
                tmpid = vnf_ids[0]
                vnfs[tmpid][VNF_KEY_TYPE] = ENDPOINT
                vnfs[tmpid][VNF_KEY_DOMAIN] = d+1
                del vnf_ids[0]
        
        # dopo avere messo in ogni dominio almeno un gateway ed almeno un endpoint si distribuiscono random gli tipi di VNFs

        random.shuffle(vnf_ids)

        for tmpid in vnf_ids:
                aType = random.choice(type_list)
                aDomain = random.choice(domain_ids)
                vnfs[tmpid][VNF_KEY_TYPE] = aType
                vnfs[tmpid][VNF_KEY_DOMAIN] = aDomain
       
        vnf_links = createVNFLinks(domains_links, vnfs)
        num_vnf_links = len(vnf_links)

        # # =======================================
        # # 			Stringification
        # # =======================================


        # stringfy domain link weights
	# ----------------------------
        str_domain_link_weights = "[|"
        for x in range(0,n_domains):
                for y in range(0,n_domains):
                        str_domain_link_weights += str(domainsCosts[x][y])+","
                str_domain_link_weights = str_domain_link_weights[:-1]
                str_domain_link_weights += "|"
        str_domain_link_weights += "]"


        # stringfy link between nodes
        # ----------------------------
        str_vnf_link = "[|"
        for i in range(len(vnf_links)):
                str_vnf_link += str(vnf_links[i][0])+","+str(vnf_links[i][1]) + "|"
        
        str_vnf_link = str_vnf_link[:-1]
        str_vnf_link += "|"
        str_vnf_link += "]"

        # stringfy vnfs
        # ----------------------------

        str_vnf = "[|"
        for x in range(0,len(vnfs)):
                for y in range(0,len(vnfs[0])):
                        str_vnf += str(vnfs[x][y])+","
                str_vnf = str_vnf[:-1]
                str_vnf += "|"
        str_vnf += "]"

        M = maxM(domainsCosts) + 1 

        out = "n_nodes = "+str(n_vnfs)+";\n"
        out += "M = "+str(M)+";\n"
        out += "n_domains = "+str(n_domains)+";\n"
        out += "domain_link_weights = "+str(str_domain_link_weights)+";\n"
        out += "num_node_links = "+str(num_vnf_links)+";\n"
        out += "node_links = "+str_vnf_link+";\n"
        out += "nodes = "+str_vnf+";\n"
        
        if (os.path.dirname(filepath)):
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w+') as outfile:
                outfile.write(out)
          

#MAIN       

if __name__ == "__main__":
        
        inp,filepath =  getSourceFile(sys.argv[1:])
        tree = ET.parse(inp)
        root = tree.getroot()
	# ----------------------------
        
        idLat = getAtrId(root.findall('.//n:key',ns),'latitude')
        idLon = getAtrId(root.findall('.//n:key',ns),'longitude')
        listOfNodes = root.findall('.//n:graph/n:node[@id]',ns)
        numbOfDomains = getNumberOfDomains(listOfNodes) #numero di domini
        domainsCosts = [[0 for x in range(numbOfDomains)] for y in range(numbOfDomains)] #lista per memorizzare il costo fra i vari domini inizializzata a zero

        #print(domainsCosts)
        listOfDomainLinks = createNodeLinks(root.findall('.//n:graph/n:edge[@source][@target]',ns))
        listOfDomainLinks.sort(key=lambda elem: elem[0])
        setDomainsCost(domainsCosts,listOfDomainLinks,listOfNodes,idLat,idLon) #genera la distanza fra i vari domini

        n_vnfs = 4*numbOfDomains

        
        #crea info riguardo ai nodi

        call_gen_map(numbOfDomains, n_vnfs, listOfDomainLinks ,domainsCosts,filepath )

        