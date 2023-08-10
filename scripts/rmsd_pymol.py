'''

pymol -c script.py -- model.pdb ref.pdb

'''


import sys
import pymol
import csv
import pandas as pd
import numpy as np

#Load structures
cplx = sys.argv[1]
ref = sys.argv[2]
cmd.load(cplx,"cplx")
cmd.load(ref,"ref")

#Align both structures

# RMSD = cmd.rms_cur("cplx and name CA","ref and name CA")
RMSD_A = cmd.rms_cur("cplx and name CA and chain A","ref and name CA and chain A")
RMSD_B = cmd.rms_cur("cplx and name CA and chain B","ref and name CA and chain B")

#Save the RMSD value
csv = open('RMSD.csv','a')
print(("%.4f,%.4f" % (RMSD_A,RMSD_B)), file = csv)
csv.close() 
