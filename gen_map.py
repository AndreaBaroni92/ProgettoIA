import xml.etree.ElementTree as ET
import sys, getopt , os
from operator import itemgetter
from geopy.distance import lonlat, distance
ns = {'n':'http://graphml.graphdrawing.org/xmlns'} #namespace


def getNumberOfDomains(root): #restituisce il numero di nodi univoci
        listOfN=[] #per avere una lista univoca
        for n in root:
                if not(n.get('id')) in listOfN:
                        listOfN.append(n.get('id'))
        return len(listOfN)

def createNodeLinks(listOfNodes): #costruisce la lista di links 
        links = []
        for n in listOfNodes:
                if not ([n.get('source'),n.get('target')] in links):
                        links.append([n.get('source'),n.get('target')])
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
        return distance(lonlat(*a), lonlat(*b)).miles

def setDomainsCost(domainsCosts,domainsLinks):
        3

#MAIN       

if __name__ == "__main__":
        
        inp =  getSourceFile(sys.argv[1:])
        tree = ET.parse(inp)
        root = tree.getroot()
        '''numbOfDomains = getNumberOfDomains(root.findall('.//n:graph/n:node[@id]',ns))
        listOfNodeLinks = createNodeLinks(root.findall('.//n:graph/n:edge[@source][@target]',ns))
        # print(listOfNodeLinks)
        #string

        # stringfy link 
	# ----------------------------
        str_vnf_link = "[|"
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
        
        print(getAtrId(root.findall('.//n:key',ns),'latitude'))
        print(getAtrId(root.findall('.//n:key',ns),'longitude'))
        print(getAtrId(root.findall('.//n:key',ns),'id'))
        numbOfDomains = getNumberOfDomains(root.findall('.//n:graph/n:node[@id]',ns))
        domainsCosts = [[0 for x in range(numbOfDomains)] for y in range(numbOfDomains)] #lista per memorizzare il costo fra i vari domini inizializzata a zero

        #print(domainsCosts)
        listOfNodeLinks = createNodeLinks(root.findall('.//n:graph/n:edge[@source][@target]',ns))
        listOfNodeLinks.sort(key=lambda elem: elem[0])
        print(listOfNodeLinks)