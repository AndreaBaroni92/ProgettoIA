'''
This script makes experiments on a set of instances,
runtime stats will be produced.
'''


from kit_run2 import run_dc


# test_nodes = range(200,201)
# test_domains = range(2,31)

#test_nodes = range(30,800,30)
#test_domains = range(10,11)
#test_nodes = range(40,100) #,odificato
test_nodes = range(30,60)
#test_domains = range(15,16)
test_domains = [18]
#dc_range = range(2,3)
dc_range = [1]
test_maps = range(1,2)
rep = 10

# test_nodes = range(150,151)
# test_domains = range(15,16)
# dc_range = range(0,16)


run_dc(test_nodes,test_domains,test_maps,rep,"chuffed",dc_range)