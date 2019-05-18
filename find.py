
import xml.etree.ElementTree as ET
import os
ns = {'n':'http://graphml.graphdrawing.org/xmlns'} #namespace
arc = []
for file1 in os.listdir("DatasetGraphml"):#legge le mappe dentro la cartella Map

    if file1.endswith(".graphml"):
        #print(file1)
        
        

        tree = ET.parse("DatasetGraphml"+os.sep+file1)
        root = tree.getroot()

        listOfNodes = root.findall('.//n:graph/n:node[@id]',ns)

        

        listofArc = root.findall('.//n:graph/n:edge[@source][@target]',ns)

        arc.append([len(listOfNodes)/len(listofArc),file1,len(listofArc),len(listOfNodes)])

       # print("nome: "+file1+" numero nodi: "+ str(len(listOfNodes))+" numero archi : "+ str(len(listofArc)))



new = sorted(arc, key=lambda x: x[0], reverse=False)

for x in new:
    print(str(x[0])," "+x[1]+" "+str(x[2])+" "+str(x[3]))