#!/usr/bin/python

import sys
import pdb
from optparse import OptionParser,OptionGroup

def correlation(snp1, snp2,numSNP):
	sum = 0
	length= len(snp1)
	for i in range(length):
		sum += snp1[i]* snp2[i]
	return sum/numSNP	

usage = """usage: %prog [options] --[tfile | bfile] plinkFileBase outfile """

parser = OptionParser(usage=usage)
basicGroup = OptionGroup(parser, "basic options")
basicGroup.add_option("--tfile", dest="tfile", 
			help="the base for a PLINK tped file")
basicGroup.add_option("--bfile", dest="bfile", 
			help="the base for a PLINK binary ped file")
basicGroup.add_option("--emmaSNP", dest="emmaFile", default=None, 
			help="\"EMMA\" file formats. This is just a text file with individuals on the rows and snps on the coumns.")
basicGroup.add_option("--emmaNumSNPs", dest="numSNPs", type="int", default=0,
			help="When providing the emmaSNP file you need to specify how many snps are in the file")
basicGroup.add_option("--candidateNum", dest="candidateNums", type="int",default=100,help="You can specify the number of candidate snp to choose from to pair with a specific snp")

basicGroup.add_option("-v", "--verbose", action="store_true", dest="verbose",
			default=False, help="print extra info")

parser.add_option_group(basicGroup)
(options, args) = parser.parse_args()
import sys
import os
import numpy as np
from pylmm import input
if len(args) != 1:
	parser.print_help()
	sys.exit()

outFile = args[0]


if not options.tfile and not options.bfile and not options.emmaFIle:
	parser.error("You mustprovide at least one PLINK input file base (--tfile or --bfile) or an emma formatted file (--emmaSNP).")

if options.verbose: sys.stderr.write("Reading PLINK input...\n")
if options.bfile: IN = input.plink(options.bfile, type='b')
elif options.tfile: IN = input.plink(options.tfile, type='t')
elif options.emmaFile: 
	if not options.numSNPs: parser.error("You must provide the number of SNPs when specifying an emma formatted file.")
	IN = input.plink(options.emmaFile,type='emma')
else: parser.error("You must provide at least one PLINK input file base (--tfile or --bfile) or an emma formatted file (--emaSNP).")

if options.emmaFile: IN.numSNPs = options.numSNPs 

IN.getSNPIterator()
print(IN.numSNPs)

numSNP = IN.numSNPs
m = 100
W = np.ones((numSNP, m))*np.nan
all_snps=[]
count=0
imputation = np.ones((numSNP,2))*np.nan
for snp,id  in IN:
	count +=1
	if options.verbose and count % 1000 ==0:
		sys.stderr.write("At SNP %d\n" % count)
	all_snps.append(snp)

indiNum= len(all_snps[0])
if(options.verbose):
	print("start to pick candidate...")
for i in range(numSNP):
	if options.verbose and i % 1000 ==0:
		sys.stderr.write("At SNP %d\n" % i)	
	correlation_coefficient= 0
	index =0
	if(i<=options.candidateNums/2):
		for j in range(min(options.candidateNums/2,numSNP-1-i)):
			new_correlation = correlation(all_snps[i], all_snps[j+i+1],numSNP)
			if(abs(new_correlation)>abs(correlation_coefficient)):
				correlation_coefficient = new_correlation
				index = j+i+1
		for k in range (i):
			if(imputation[k][1]==i):
				if(abs(imputation[k][0])>abs(correlation_coefficient)):
					correlation_coefficient = imputation[k][0]
					index =k
	elif(i<numSNP-options.candidateNums/2):
		index=k
		for j in range(options.candidateNums/2):
			snp2 = i - options.candidateNums/2 +j
			if(imputation[snp2][1]==i):
				if(abs(imputation[snp2][0])>abs(correlation_coefficient)):
					correlation_coefficient = imputation[snp2][0]
					index = snp2
			snp3 = i + j +1
			new_correlation = correlation(all_snps[i],all_snps[snp3],numSNP)
			if(abs(new_correlation)>abs(correlation_coefficient)):					
				correlation_coefficient = new_correlation
				index = snp3
	else:
		for j in range(options.candidateNums/2):
			snp2 = i-options.candidateNums/2+j
			if(imputation[snp2][1]==i):
				if(abs(imputation[snp2][0])>abs(correlation_coefficient)):
					correlation_coefficient =imputation[snp2][0]
					index=snp2
		for k in range(numSNP- i -1):
			snp2= i +k+1
			new_correlation = correlation(all_snps[i], all_snps[snp2],numSNP)
			if(abs(new_correlation)>abs(correlation_coefficient)):
				correlation_coefficient = new_correlation
				index= snp2
	imputation[i][0]= correlation_coefficient
	imputation[i][1]= index					
#	print(i)
#	print(index)
#	print(correlation_coefficient)
#print(all_snps)
np.savetxt(outFile, imputation)

	

