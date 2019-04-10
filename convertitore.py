from jsonschema import validate
from S import schemaRequest,schemaDomConst
import sys, getopt , os
import json

dic = {"WANA":2,"DPI":1,"TS":3,"VPN":4,"NAT":5,"ENDPOINT":10}


def reqToArc(req,dupList):
	parts = req.split(",")
	translated = []
	s = 1
	for p in range(1,len(parts)):
		translated.append([s,p+1])
		if parts[p] not in dupList:
			s = (p+1)
	return translated

def boolToStr(inp):#aggiungo 0 all'inizio e alla fine perche' perche' si devono considerare gli ENDPOINT  sui quali non so è assunto niente

    out = [int(i ==True ) for i in inp]
    st = "[0,"

    for i in range(len(out)):
        st += str(out[i])+","
 
    st += "0]"

    return st

#come richiesto dal modello e' necessario aggiungere un endpoint all' inizio e alla fine della lista dei vnf che ha numero 10
# la funzione seguente converte la lista dei vnf in formato json nel formato adatto per .dzn
def vnfToString(listOfVnf):
    global dic
    out = "[10,"

    for x in listOfVnf:
        out += str(dic[x])+","
    
    out += "10]"
    return out

def createDupList(listOfDupVnf):
    global dic

    out = ""
    for x in listOfDupVnf:
        out+=str(dic[x])+","

    out = out[:-1]

    return out

def domainConstraintsToModel(listOfConst):

    global dic

    lenListOfConst = len(listOfConst)

    if lenListOfConst == 0:
        return str(1),"[|0,0,0,0|]"
    else:
        out = "[|"
        for i in range(lenListOfConst):#vengono settati i vari parametri 0 = numero dominio, 1= tipo vnf, 2= min, 3 = max
            out += str(listOfConst[i][0])+","+ str(dic[listOfConst[i][1]])+ ","\
            +  str(listOfConst[i][2])+","+  str(listOfConst[i][3]) +"|"
        out +="]"
        return str(lenListOfConst),out

#serve per controllare i file passati come input
def getSourceFile(argv):
        request  = ''
        dConstraints=''
        outputfile = ''
        if len(sys.argv) <= 6:
                print('convertitore.py -r <request> -c <domain_constraints> -o <output_file> ')
                sys.exit(1)
        try:
             opts ,args= getopt.getopt(argv,"hr:c:o:")
        except getopt.GetoptError:
                print ('convertitore.py -r <request> -c <odomain_constraints> -o <output_file> ')
                sys.exit(2)
        for opt, arg in opts:
                if opt == '-h':
                        print ('convertitore.py -r <request> -c <odomain_constraints> -o <output_file>')
                        sys.exit()
                elif opt in ("-r"):
                        request = arg
                        if not (os.path.isfile(request)):
                                print("file "+ request+ " doesn't exist")
                                sys.exit(1)
                elif opt in ("-c"):
                        dConstraints = arg
                        if not (os.path.isfile(dConstraints)):
                                print("file "+ dConstraints+ " doesn't exist")
                                sys.exit(1)
                elif opt in ("-o"):
                        outputfile = arg

        return request ,dConstraints, outputfile


#MAIN       

if __name__ == "__main__":

    req, dConst, fileOut = getSourceFile(sys.argv[1:])

    with open(req) as inpReq:  
        requestObject = json.load(inpReq)

    with open(dConst) as inpConst:  
        constList = json.load(inpConst)

    validate(requestObject, schemaRequest ) #convalida il formato json delle richieste secondo lo schema definito nell'articolo
    validate(constList, schemaDomConst ) #convalida il formato json dei domain constraint secondo lo schema definito nell'articolo

    vnfarcs= reqToArc(vnfToString(requestObject["vnfList"]).strip('[]'), createDupList(requestObject["dupList"]) )


    #viene convertito in formato .dzn  il request-Tree
    str_vnf_arcs = "[|"
    for x in range(0,len(vnfarcs)):
        for y in range(2):
            str_vnf_arcs += str(vnfarcs[x][y])+","
        str_vnf_arcs = str_vnf_arcs[:-1]
        str_vnf_arcs += "|"
    str_vnf_arcs += "]"


    nDom , nDomString = domainConstraintsToModel(constList)

    out = "start_domain = "+str(requestObject["src"])+";\n"
    out += "target_domain = "+ str(requestObject["dst"])+";\n"
    out += "vnflist_size = "+ str (len(requestObject["vnfList"]) + 2)+";\n" #2 perche' si contano gli endpoint
    out += "vnfList = "+ vnfToString(requestObject["vnfList"])+";\n" #lista dei vnf con l'aggiunta degli ENDPOINT  all' inizio e alla fine
    out += "vnf_arcs = "+ str_vnf_arcs +";\n"# request-Tree
    out += "proximity_to_source = " + boolToStr(requestObject["prox_to_src"]) +";\n"
    out += "proximity_to_destination = " + boolToStr(requestObject["prox_to_dst"]) +";\n"
    out += "n_domain_constraints = " + nDom +";\n"
    out += "domain_constraints = " + nDomString + ";\n"


    if (os.path.dirname(fileOut)):
        os.makedirs(os.path.dirname(fileOut), exist_ok=True)

    with open(fileOut, 'w+') as outfile:
        outfile.write(out)


