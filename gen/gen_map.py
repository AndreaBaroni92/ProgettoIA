import xml.etree.ElementTree as ET
import sys, getopt , os
import random
import json
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

def filterNode(listOfNodes,idLat,idLon):#serve per filtrare i nodi che hanno la latitudine e la longitudine

        ris = []

        nodeLat="n:data[@key='$1']"
        nodeLon="n:data[@key='$2']"
        nodeLat=nodeLat.replace("$1",idLat)
        nodeLon=nodeLon.replace("$2",idLon)

        for n in listOfNodes:
                if len(n.findall(nodeLat,ns)) == len(n.findall(nodeLon,ns)) == 1:#se la condizione e' vera sono preseni due nodi con latitudine e long
                        ris.append(n)
        
        return ris




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

def createNodeLinks(listOfNodes, nodesWithLonAndLat): #costruisce la lista di links 
        links = []

        for a,b in enumerate(nodesWithLonAndLat):
                for c,d in enumerate(nodesWithLonAndLat):
                        
                        for n in listOfNodes:
                                if int(n.get('source'))==b and int(n.get('target'))==d:
                                       # print("--"," ",b," ",d,"--")

                                        if not([a+1,c+1] in links):
                                                links.append([a+1,c+1])
                                               # print("--2"," ",a+1," ",c+1,"--2")




        '''for n in listOfNodes:
                if int(n.get('source')) in nodesWithLonAndLat and int(n.get('target')) in nodesWithLonAndLat:#solo i nodi che hanno latitudine e longitudine vengono inseriti 
                        s =abs(int(n.get('source'))) +1  # +1 perche' non e' possibile avere un indice 0
                        t = abs(int(n.get('target'))) +1 
                        if not ([s,t] in links):
                                links.append([s,t])
#                else:
#                       print(n.get('source'))'''
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
                        

def setDomainsCost(domainsCosts,domainsLinks,listOfNodes,nodesWithLonAndLat,idLat,idLon):
        for i in range(len(domainsCosts)):
                for j in range(len(domainsCosts)):
                        if i == j:
                                domainsCosts[i][j] = 0

        for a, b in enumerate(nodesWithLonAndLat):
                for c,d in  enumerate(nodesWithLonAndLat):
                        if [a+1 ,c + 1 ] in domainsLinks:
                                
                                x = getInfo(b,listOfNodes,idLon)
                                y = getInfo(b,listOfNodes,idLat)
                                z = getInfo(d,listOfNodes,idLon)
                                w = getInfo(d,listOfNodes,idLat)
                                ris = getDistance((x,y),(z,w))
                                
                                domainsCosts[a][c]= ris



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


def stringification(n_domains,n_vnfs,domainsCosts,vnf_links,vnfs,M,num_vnf_links):#converte in formato .dzn

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

        

        out = "n_nodes = "+str(n_vnfs*n_domains)+";\n"
        out += "M = "+str(M)+";\n"
        out += "n_domains = "+str(n_domains)+";\n"
        out += "domain_link_weights = "+str(str_domain_link_weights)+";\n"
        out += "num_node_links = "+str(num_vnf_links)+";\n"
        out += "node_links = "+str_vnf_link+";\n"
        out += "nodes = "+str_vnf+";\n"
        
        return out




def call_gen_map(n_domains,n_vnfs,domains_links,domainsCosts,filepath):
        global VNF_KEY_TYPE,VNF_KEY_DOMAIN,GATEWAY,ENDPOINT,WANA,SHAPER,DPI,type_list

        vnf_ids = list(range(n_vnfs*n_domains))
        #domain_ids = range(1,n_domains + 1)
        vnfs = initVNFs(vnf_ids)

        # i nodi da 0 a n_domains -1 sono di tipo GATEWAY (per ogni dominio deve esserci almeno un GATEWAY)

        for d in range(n_domains): 
                tmpid = vnf_ids[0]
                
                vnfs[tmpid][VNF_KEY_TYPE] = GATEWAY
                vnfs[tmpid][VNF_KEY_DOMAIN] = d + 1
                del vnf_ids[0]
        
        # i nodi da n_domains  a  2*n_domains -1  sono di tipo ENDPOINT (per ogni dominio deve esserci almeno un ENDPOINT)

        for d in range(n_domains): 
                tmpid = vnf_ids[0]
                vnfs[tmpid][VNF_KEY_TYPE] = ENDPOINT
                vnfs[tmpid][VNF_KEY_DOMAIN] = d+1
                del vnf_ids[0]
        
        # dopo avere messo in ogni dominio almeno un gateway ed almeno un endpoint si distribuiscono random gli tipi di VNFs

        random.shuffle(vnf_ids)

        # per ogni dominio metto n_vnfs - 2 vnfs in quanto endpont e gateway sono gia' assegnati
       
        for d in range(n_domains):
                for i in [0]*(n_vnfs-2):
                        tmpid = vnf_ids[i]
                        aType = random.choice(type_list)
                        vnfs[tmpid][VNF_KEY_TYPE] = aType
                        vnfs[tmpid][VNF_KEY_DOMAIN] = d+1
                        del vnf_ids[i]
        

        '''
       for tmpid in vnf_ids:
                aType = random.choice(type_list)
                aDomain = random.choice(domain_ids)
                vnfs[tmpid][VNF_KEY_TYPE] = aType
                vnfs[tmpid][VNF_KEY_DOMAIN] = aDomain
       '''

        vnf_links = createVNFLinks(domains_links, vnfs)
        num_vnf_links = len(vnf_links)

        # # =======================================
        # # 			Stringification
        # # =======================================

        M = maxM(domainsCosts)  

        out = stringification(n_domains,n_vnfs,domainsCosts,vnf_links,vnfs,M,num_vnf_links)

        outJs= {"n_nodes":len(vnfs),
                "M":M,
                "n_domains":n_domains,
                "domain_link_weights": domainsCosts,
                "num_node_links":num_vnf_links,
                "node_links":vnf_links,
                "nodes":vnfs
        }

        filepathjs= os.path.splitext(filepath)[0]+".json" #recupera solo il nome di filepath senza estensione


        
        if (os.path.dirname(filepath)):
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w+') as outfile:
                outfile.write(out)

        with open(filepathjs, 'w+') as outfile1:
                outfile1.write(json.dumps(outJs))



def generateMap(inp,filepath,n_vnfs ): #genera la mappa in formato .dzn prendendo in input la mappa in formato graphml e il numero di vnfs per dominio
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
        domainsCosts = [[-1 for x in range(numbOfDomains)] for y in range(numbOfDomains)] #lista per memorizzare il costo fra i vari domini inizializzata a -1
        # il -1 serve in quanto serve per evidenziare i domini che non hanno connessioni


        #print(domainsCosts)
        nodesWithLonAndLat = [ int(x.get("id")) for x in listOfNodes]
        
        listOfDomainLinks = createNodeLinks(root.findall('.//n:graph/n:edge[@source][@target]',ns),nodesWithLonAndLat)#TODO inserire solo i link i cui estremi sono dei nodi che hanno long e lat
        #listOfDomainLinks.sort(key=lambda elem: elem[0])

        #for s,f in enumerate(nodesWithLonAndLat):
        #        print(s," --> ",f)

        setDomainsCost(domainsCosts,listOfDomainLinks,listOfNodes,nodesWithLonAndLat,idLat,idLon) #genera la distanza fra i vari domini

        maxCost= maxM(domainsCosts)

        #i domini che non hanno connessioni fra di loro (peso -1) vengono settati al massimo costo fra i vari domini

        for i in range(len(domainsCosts)):
                for j in range(len(domainsCosts[i])):
                        if domainsCosts[i][j]== -1:
                                domainsCosts[i][j]= maxCost
 
        #crea info riguardo ai nodi

        call_gen_map(numbOfDomains, n_vnfs, listOfDomainLinks ,domainsCosts,filepath )

        

        



#MAIN       

if __name__ == "__main__":
        
        inp,filepath =  getSourceFile(sys.argv[1:])

        generateMap(inp,filepath,3)