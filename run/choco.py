'''
This script makes experiments on a set of instances,
runtime stats will be produced.
'''


from kit_run import run_dc


# test_nodes = range(200,201)
# test_domains = range(2,31)

test_nodes = range(30,800,30)
test_domains = range(10,11)
dc_range = range(2,3)
test_maps = range(1,11)
rep = 10

# test_nodes = range(150,151)
# test_domains = range(15,16)
# dc_range = range(0,16)


run_dc(test_nodes,test_domains,test_maps,rep,"choco",dc_range)