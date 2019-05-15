'''
This script makes experiments on a set of instances,
runtime stats will be produced.
'''


from kit_run import run,run_dc


# test_nodes = range(100,101)
# test_domains = range(2,31)

test_nodes = range(30,811,30)
test_domains = range(10,11)

test_maps = range(1,11)
rep = 10

# filesufix = "data-exp-n"+str(test_nodes[0])
filesufix = "data-exp-d"+str(test_domains[0])
run_dc(test_nodes,test_domains,test_maps,rep,filesufix,"gecode")