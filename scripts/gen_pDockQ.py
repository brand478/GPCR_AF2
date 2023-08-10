'''
mutated script to get pDockQ for AFmultimer
source code from Arne in Sthlm
update: 2023/12/04
'''

import sys
import numpy as np
import argparse
import csv
from Bio.PDB import PDBIO
from Bio.PDB.MMCIFParser import MMCIFParser
from Bio.PDB.PDBParser import PDBParser

def pDockQ(structure,cutoff,disocut1=50,disocut2=70,disocut3=90):
    i=0
    tiny=1.e-20
    chains=[]
    for chain in structure.get_chains():
        chains+=[chain]
        i+=1
        #print (chains)
    interface_residues1=[]
    interface_residues2=[]
    for res1 in chains[0]:
        for res2 in chains[1]:
            #Atom-atom distance
            #print (res1,res2)
            test=False
            for i in res1:
                if test:break
                for j in res2:
                    dist = np.linalg.norm(i.coord - j.coord)
                    #scipy.spatial.distance.euclidian
                    #dist = distance.euclidean(coords[i], coords[len(ch1_res_nos)+j]) #Need to add l1 to get the right coords
                    if dist < cutoff:
                        #Save residues
                        #print ("Appending",res1,res2)
                        interface_residues1.append(res1.id[1])
                        interface_residues2.append(res2.id[1])
                        test=True
                        break
                    elif dist > 2*cutoff: # To speed up things
                        test=True
                        break

    #print (interface_residues1,interface_residues2)
    #print (np.unique(interface_residues1),np.unique(interface_residues2))
    #interface_res_num.append(np.unique(interface_residues).shape[0])
    #atoms, residue_numbers, coords = np.array(atoms), np.array(residue_numbers), np.array(coords)
    if1=np.unique(interface_residues1)
    if2=np.unique(interface_residues2)
    NumRes=if1.shape[0]+if2.shape[0]
    i=tiny
    b=0
    b1=0
    b2=0
    i1=0
    i2=0
    NumDiso1=[0,0,0,0]
    NumDiso2=[0,0,0,0]
    for res in chains[0]:
        b1+=res['CA'].get_bfactor()
        i1+=1
        if res['CA'].get_bfactor()>disocut3: # >90
            NumDiso1[0]+=1
        elif res['CA'].get_bfactor()>disocut2: # 70-90
            NumDiso1[1]+=1
        elif res['CA'].get_bfactor()>disocut1: # 50-70
            NumDiso1[2]+=1
        else: # <50
            NumDiso1[3]+=1
        if res.id[1] in if1:
            b+=res['CA'].get_bfactor()
            i+=1
    for res in chains[1]:
        b2+=res['CA'].get_bfactor()
        i2+=1
        if res['CA'].get_bfactor()>disocut3: # >90
            NumDiso2[0]+=1
        elif res['CA'].get_bfactor()>disocut2: # 70-90
            NumDiso2[1]+=1
        elif res['CA'].get_bfactor()>disocut1: # 50-70
            NumDiso2[2]+=1
        else: # <50
            NumDiso2[3]+=1
        if res.id[1] in if2:
            b+=res['CA'].get_bfactor()
            i+=1
    IF_plDDT=b/i
    plDDT1=b1/i1
    plDDT2=b2/i2
    #print ("test",b,b1,b2,i,i1,i2,NumDiso1,NumDiso2)
    #Get res nos
    #Get chain cut
    #ch1_res_nos = np.argwhere(residue_numbers<=l1)[:,0] #All residue numbers
    #ch2_res_nos =  np.argwhere(residue_numbers>l1)[:,0]
    
    #print (NumRes,IF_plDDT)
    return (NumRes,IF_plDDT,plDDT1,plDDT2,NumDiso1,NumDiso2,i1,i2)

def sigmoid(x, L ,x0, k, b):
    y = L / (1 + np.exp(-k*(x-x0)))+b
    return (y)

arg_parser = argparse.ArgumentParser(description="Calculates pDockQ from NumRes and IF_plDDT")
arg_parser.add_argument("-p","--pdb",type=argparse.FileType('r'),help="Input pdb file pLddt values in bfactor columns")
arg_parser.add_argument("-F","--factor", type=float,required=False,default=1.0,help="Factor to multiply B-factor for (sometimes 100)")
arg_parser.add_argument("-C","--cutoff", type=float,required=False,default=10.0,help="Cutoff for defining distances")
arg_parser.add_argument("-i","--IF_plDDT", type=float,required=False,help="Average plDDT in interface residues")
args = arg_parser.parse_args()

cutoff=args.cutoff
# used in Interaction studies.
# cutoff <=10:
#10 SpearmanrResult(correlation=0.7330653937901442, pvalue=7.988440779428826e-246)
popt=[7.07140240e-01, 3.88062162e+02, 3.14767156e-02, 3.13182907e-02]

Name = args.pdb.name # Get the name of the input pdb file

bio_parser = PDBParser()
structure_file = args.pdb
structure_id = args.pdb.name[:-4]
structure = bio_parser.get_structure(structure_id, structure_file)
NumRes,IF_plDDT,plDDT1,plDDT2,Diso1,Diso2,len1,len2=pDockQ(structure,cutoff)
# print(NumRes,IF_plDDT,plDDT1,plDDT2,Diso1,Diso2,len1,len2)
tiny=1.e-20

pDockQ_score=sigmoid(np.log(NumRes+tiny)*IF_plDDT*args.factor,*popt)

pDOCKQ = np.round(pDockQ_score,3)
print(structure_id)
print(pDOCKQ)
# with open('pDockQ.csv','a',newline='') as fin:
#     writer = csv.writer(fin)
#     writer.writerow([pDOCKQ])