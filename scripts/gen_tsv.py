'''
script for generate tsv file for each structure
Date: 2022/12/15

python gen_tsv.py -top pdbfile -traj file.dcd -i file.tsv

'''

import os
import argparse as ap


def getArguments():

    parser = ap.ArgumentParser(description='generate tsv file for the input structure')
    required = parser.add_argument_group('required arguments')
    optional = parser._action_groups.pop()
    parser._action_groups.append(optional) 

    required.add_argument('--topology', '-top',
                          required=True,
                          type=str, 
                          default=None, 
                          help='import the pdb file to get the interaction between protein and peptide')  
    required.add_argument('--trajectory', '-traj', 
                          required=True,
                          type=str, 
                          default=None, 
                          help= 'name of trajectory file, for example:4GRV_2022.dcd,4GRV_ref.dcd,4GRV_notmp.dcd')
    required.add_argument('--interaction', '-i', 
                          required=True,
                          type=str, 
                          default=None, 
                          help= 'name of tsv file, for example:4GRV_2022_rank0.tsv')                   
    args = parser.parse_args()

    return args


def get_trajectory(pdb_file):

    args = getArguments()
    
    pdb_file = args.topology
    file_path = 'Get_interaction/trajectory'
    dcd_file_name = args.trajectory
    dcd_file = os.path.join(file_path, dcd_file_name)

    cmd1 = f'/proj/berzelius-2021-85/users/x_zeych/software/miniconda3/envs/py37/bin/mdconvert {pdb_file} -o {dcd_file}'
    os.system(cmd1)
    return dcd_file


def main():

    args = getArguments()
   
    pdb_file = args.topology
    dcd_file = get_trajectory(pdb_file)

    file_path = 'Get_interaction'
    tsv_file_name = args.interaction
  
    tsv_file = os.path.join(file_path, tsv_file_name)

    cmd2 = f'get_dynamic_contacts.py --topology {pdb_file} \
                            --trajectory {dcd_file} \
                            --output {tsv_file} \
                            --sele "chain A" \
                            --sele2 "chain B" \
                            --itypes all'
    os.system(cmd2)

 


if __name__ == '__main__':

    main()