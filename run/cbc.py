'''
This script makes experiments on a set of instances,
runtime stats will be produced.
'''


from kit_cbc import run_dc

test_nodes = range(300,301)
test_domains = range(3,31)
test_maps = range(1,11)
# rep = 10
# dc_range = range(2,3)
# filesufix = "data-exp-n"+str(test_nodes[0])

# test_nodes = range(30,800,30)
# test_domains = range(10,11)
dc_range = range(2,3)
# test_maps = range(1,11)
rep = 10

run_dc(test_nodes,test_domains,test_maps,rep,"cbc",dc_range)