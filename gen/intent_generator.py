# this file generates 'n' simulated requests

import glob
import sys
from random import randint,sample
import os

def reqToNum(req,dic):
	parts = req.split(",")
	translated = []
	for p in parts:
		translated.append(str(dic[p]))
	return ",".join(translated)


def reqToArc(req,dupList):
	parts = req.split(",")
	translated = []
	s = 1
	for p in range(1,len(parts)):
		translated.append([s,p+1])
		if parts[p] not in dupList:
			s = (p+1)
	return translated

def generateProximity(req,pairList):
	checker = False
	parts = req.split(",")
	p_to_s = [0 for x in range(len(parts))]
	p_to_d = [0 for x in range(len(parts))]
	for pair in pairList:
		if pair in parts:
			indices = [i for i, x in enumerate(parts) if x == pair]
			p_to_s[indices[0]] = 1
			p_to_d[indices[1]] = 1
			checker = True

	if not checker: # maybe do some random
		a = randint(0,len(parts)-1)
		b = randint(0,len(parts)-1)
		if a < b and a != len(parts)-1:
			if a !=0:
				p_to_s[a] = 1
			if b !=0:
				p_to_d[b] = 1
		else:
			c = randint(0,1)
			if c == 0 and a != len(parts)-1:
				p_to_s[a] = 1
	return p_to_s,p_to_d


def loadRequests():
	parts = os.path.abspath(__file__).split(os.sep)
	parts = parts[:-1]
	expdir = (os.sep).join(parts)
	with open(expdir+os.sep+"vnflists.txt", 'r') as content_file:
	    lines = content_file.readlines()
	requests = []
	for line in lines:
		wrap_line = line.strip()
		requests.append(wrap_line)
	return requests

def requestToVar(req):
	global pairList
	#vnflist = reqToNum(req,dic)
	#vnfarcs = reqToArc(req,dupList)
	p_to_s,p_to_d = generateProximity(req,pairList)
	p_to_s = [x==1 for x in p_to_s]
	p_to_d = [x==1 for x in p_to_d]

	return p_to_s,p_to_d 

dic = {"WANA":2,"DPI":1,"SHAPER":3,"VPN":4,"NAT":5,"ENDPOINT":10}
dupList = ['DPI']
pairList = ['WANA','VPN']

# print 'Example of usage:'
# requests = loadRequests()
# reqIdx = randint(0,len(requests)-1)
# vnflist,vnfarcs,p_to_s,p_to_d  = requestToVar(requests[reqIdx])
# print vnflist
# print vnfarcs
# print p_to_s
# print p_to_d


# test
# for req in requests:
# 	print req
# 	vnflist,vnfarcs,p_to_s,p_to_d  = requestToVar(req)
# 	print vnflist
# 	print vnfarcs
# 	print p_to_s
# 	print p_to_d



