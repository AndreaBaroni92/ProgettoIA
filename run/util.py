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

        

        out = "n_nodes = "+str(n_vnfs)+";\n"
        out += "M = "+str(M)+";\n"
        out += "n_domains = "+str(n_domains)+";\n"
        out += "domain_link_weights = "+str(str_domain_link_weights)+";\n"
        out += "num_node_links = "+str(num_vnf_links)+";\n"
        out += "node_links = "+str_vnf_link+";\n"
        out += "nodes = "+str_vnf+";\n"
        
        return out

