'''
script to assess the prediction
LOC: Jens Carlsson's Lab, Scilife lab, BMC, Uppsala University
Author: Zeyu Cheng
date: 2022/11/28
update to : 2023/12/04

python analysis.py aligned_folder_name match_interaction_file
'''


import os
import sys
import csv
from glob import glob 
import pandas as pd 
import subprocess


folder_name = sys.argv[1]
PDBcode = folder_name.split('_')[-3]    # get the PDB code
# template = str(folder_name.split('_')[-2])   # get the template 
template = 'notmp'
# match_interaction_file = sys.argv[2]
dst_dir_path = '/proj/berzelius-2021-85/users/x_zeych/Analysis_Result'   # Make a new file to store the csv file
if not os.path.exists(dst_dir_path): os.mkdir(dst_dir_path)

os.chdir(folder_name) # change the work directory to the aligned folder
pdb_list = sorted(glob('ali_*.pdb'))   #get the files name
pdb_list_org = sorted(glob('rank_*.pdb'))
refPDB = 'Ref.pdb' 

# Make the documental file
with open('document.csv','a',newline='') as fin:
    writer = csv.writer(fin)
    for pdb in pdb_list:
        
        pdb_name=str(pdb)
        filename = os.path.splitext(pdb_name)[0]  #split the extension
        rank   = int(filename.split('_')[2])   # get the ranking number
        cscore  = filename.split('_')[3]   # get the confidence score
        writer.writerow([PDBcode,template,rank,cscore])

#Fix the residue number   
for pdb in pdb_list:
    # Get RMSD
    cmd1 = '/proj/berzelius-2021-85/users/x_zeych/software/miniconda3/envs/py37/bin/pymol -c /proj/berzelius-2021-85/users/x_zeych/rmsd_pymol.py -- ' + pdb + ' ' + refPDB
    os.system(cmd1) 
    cmd2 = f'/proj/berzelius-2021-85/users/x_zeych/software/DockQ/scripts/fix_numbering.pl {pdb} {refPDB}'
    os.system(cmd2)
    fixedmodelPDBs = sorted(glob('ali_*.fixed'))

# Get the DockQ Score 
for fixedmodel in fixedmodelPDBs:
    
    cmd3 = '/proj/berzelius-2021-85/users/x_zeych/software/DockQ/DockQ.py -short ' + fixedmodel + ' ' + refPDB
    os.system(cmd3)

# Get the pDockQ score

for pdb in pdb_list_org:
    
    cmd4 = f'python3 /proj/berzelius-2021-85/users/x_zeych/getpDockQ.py -p {pdb}'
    os.system(cmd4)

# Get the GDT score
# First generate input file of the GDT analysis, a file 'pdb1.pdb2' stored in sbdir MOL2
LGA_path = '/proj/berzelius-2021-85/users/x_zeych/LGA_package_src/MOL2'

def GDT_score(file):
    with open(file, 'r') as f_ts :
        for line in f_ts:
            elements = line.split()
            if 'GDT PERCENT_AT' in line:
                TS_score = (float(elements[3])+float(elements[5])+float(elements[9])+float(elements[17]))/4.0 # GDT_TS=($4+$6+$10+$18)/4.0
                GDT_ts = '{:6.2f}'.format(TS_score)
                return(GDT_ts)

for pdb in pdb_list:
    noextension = os.path.splitext(pdb)[0]  #split the extension
    rank_number   = noextension.split('_')[2]   # get the ranking number
    GDT_input = f'{PDBcode}_{template}_{rank_number}'
    output_file = os.path.join(LGA_path, GDT_input)

    
    with open(pdb,'r') as predict, open(refPDB,'r') as ref:
        content = f'MOLECULE   {predict}\n{predict.read()}MOLECULE  {ref}\n{ref.read()}'
    with open(output_file, 'w') as fin:
        fin.write(content)
    # Then LGA pragramme
    # Calculate structural alignment for GDC_TS and GDC_HA
    shell_script = '/proj/berzelius-2021-85/users/x_zeych/genGDT.sh'
    subprocess.run(['/bin/bash', shell_script, '../LGA_package_src/', GDT_input], check = True)

    # Write the GDT_ts score into a csv file
    gdc_ts_file = f'/proj/berzelius-2021-85/users/x_zeych/LGA_package_src/{GDT_input}.gdc_ts_ha'

    GDT_TS = GDT_score(gdc_ts_file)
    print(GDT_TS)
    with open('GDT.csv','a',newline='') as f_GDT:
        writer = csv.writer(f_GDT)
        writer.writerow([GDT_TS])

# # Get Fbur score
df = pd.read_csv(f'/proj/berzelius-2021-85/users/x_zeych/{match_interaction_file}')

with open('Fbur.csv','a',newline='') as fin:
    writer = csv.writer(fin)
    for index, row in df.iterrows():
        true_positive = row.astype(str).str.count('yes').sum()
        tp =true_positive.sum()
        Fbur = round(true_positive/(df.shape[1]-1),3)
    
        writer.writerow([Fbur])

# combine all the csv files int one
inputfile_csv_1 = "document.csv"
inputfile_csv_2 = "pDockQ.csv"
inputfile_csv_3 = "DockQ.csv"
inputfile_csv_4 = "Fbur.csv"
inputfile_csv_5 = "RMSD.csv"
outputfile      = "result.csv"
csv_1 = pd.read_csv(inputfile_csv_1)
csv_2 = pd.read_csv(inputfile_csv_2)
csv_3 = pd.read_csv(inputfile_csv_3)
csv_4 = pd.read_csv(inputfile_csv_4)
csv_5 = pd.read_csv(inputfile_csv_5)
out_csv = pd.concat([csv_1,csv_2,csv_3,csv_4,csv_5],axis=1)
out_csv = pd.concat([csv_1,csv_2,csv_3,csv_5],axis=1)
out_csv.to_csv(outputfile,index=False)

#add the headers
# data=pd.read_csv(r'result.csv',header=None,names=['PDBcode','template','Rank','confidence','GDT_ts','DockQ','Fbur','RMSD_A','RMSD_B'])
data=pd.read_csv(r'result.csv',header=None,names=['PDBcode','template','Rank','confidence','pDockQ','DockQ','RMSD_A','RMSD_B'])

data.to_csv('result.csv',index=False)
cmd5 = 'cp result.csv /proj/berzelius-2021-85/users/x_zeych/Analysis_Result/' + PDBcode + '_'+template +'.csv'
os.system(cmd5)
