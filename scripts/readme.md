----------------------
Alphafold Benchmarking
----------------------
# Thesis Project 2020/11-2023/6 in Carlsson Lab
# Update to 2023-2-3
# Workflow
-------------
-------------
Preparation
-------------
	From PDB download .pdb and .FASTA file for protein-peptide comlexes.

	Before running AlphaFold_v2, make sure that the fasta files as input sequences are identical with PDB files.
	The fasta files have the format below:
		>sequence_1
		PROTEIN
		>sequence_2
		PEPTIDE

	In reference PBD files, the name for GPCR chain should be A , and for peptide should be B:
	python Rename_chains.py pdb_file L:A R:B ....
	
	Also the residue number of peptide should start from 1. This can be made in pymol:
	> alter (chain B), resi=str(int(resi)+4)

	Finally, add hydrogen atoms for reference PDB, this is essential for the interaction analysis:
	conda activate AmberTools22
	reduce old > new
	To find more instructions see ambertools user guide section about reduce


Step 1 : generate AlphaFold_v2 predictions
--------------------------------------------
	Firstly generate the batch files:
	python genAF2_v2.py \
		-s sequences/input_sequence.fasta \
		-m 5 \
		-c 1 \
		-t 2016
	Parameters:
		-models/-m : Number of models to generate for AlphaFold_Multimer, it will generate 5 multimers for each model, 
						so one will get 5*m models in total.
		-chunks/-c : Number of singularities per submit file. For example, -m 1000 -c 10 refers to 1000 models, put in 200/(10*5)= 4 *.sh files.
		-template/-t : Input a date to determine whether pair representation will be searched. If not none, the AlphaFold will not search any 
						structures released after the date. Therefore, input a date which is later than release date if the tempalte is wanted, 
						Default setting is 1975-11-01. A date before the release date of the certain protein could be input as the 'Half template',
						Under this situation alphafold 2 will search similar structures but not the same one, so that it won't be 'cheating' in this way.
	Generate them all: 
	for f in fasta_AF2/*_reduced.fasta; do python genAF2_v2.py -s $f -m 5 -c 1;done;
	for f in fasta_AF2/*_reduced.fasta; do python genAF2_v2.py -s $f -m 5 -c 1 -t 2022;done;
	
	for alphaofld version 2.3:
	run python genAF2_v2.3.py, configuration -dropout -recyclenumber:
	for f in fasta_file; do python genAF2_v2.3.py -s $f -m 5 -c 1 -dropout -maxrecycles 9;done;   $

	Then submit the job to cluster:		 
	sbatch submit_*.sh  
	Submit them all : for f in *.sh; do sbatch $f; done;
	cancel all the jobs: squeue -u x_zeych -h | awk '{print $1}' | xargs scancel
	check the job : squeue -u x_zeych
	sinfo
	projinfo

Before following steps, change the environment:
conda activate py37

Step 2 : Prepare the data for more analysis 
---------------------------
	a. Align xtrl and predition:
	python Align.py -f AlphaFold_prediction_folder/ \
		-n numers_of-models \
		-r reference_PDB.pdb

	A folder called 'aligned_pdbcode_template_number_of_models' will be generated
	When there are more than one folders for one protein, t.ex when 1000 models are predicted:
	for f in AF2_foler; do python gather1000.py -f $f -r ref.pdb; done;     $
	A folder called 'aligned_pdbcode_template_1000' will be made,and then align it:
	python Align1000.py aligned_pdbcode_template_1000
	b. Preparation the interaction(See step 3 below)


Step 3 : Analysis the interaction.
----------------------------------
	'''make a trajectory file using models. OBS! This step is unnecessary.
		the script geninteraction.py is for generating a trajectory file using all the models as different time-scale 
		confrontation. So far a directory for trajectory file traj.pdb wil be made.'''
		python gentraj.py 

	a. Get interactions for each protein
		In this step the interaction of protein-peptide will be analyzed. Here we used a package 'GetContacts':
		https://github.com/getcontacts/getcontacts
		The interaction information will be stored in a tsv file, in order to get this file, run the command:
		python gen_tsv.py --topology .pdb \
			--trajectory .dcd  \
			--interaction .tsv
		Parameter: --topology/-top : pdb file which is the input to get the interaction.
				   --trajectory/-traj : a dcd format file storing the trajectory information of the PDB, input the name manually
				   					here MDTraj package is used, and the command has been already embedded in gen_tsv.py:
									mdconvert aligned_7AUE_AF2_reduced_2022_0/Ref.pdb -o ref.dcd
				   --interaction/-i : input the name manually. Now use the trajectory and the pdb to get the interaction.
									here script used is get_dynamic_contacts.py, which compute all interactions formed at a protein-protein interface throughout simulation specifically,
									The command is also embedded in the major script:
									get_dynamic_contacts.py --topology TOP.pdb \
                            		--trajectory TRAJ.nc \
                            		--output protein_interface_all.tsv \
                            		--cores 12 \
                            		--sele "chain A" \
                            		--sele2 "chain B" \
                            		--itypes all
									In the parameter, chain A stands for the protein, and chain B stands for the peptide, interaction type can also be specified.

	b. Visualization
		The interaction can be visualized by flareplot or atlas :
		Flareplot : https://gpcrviz.github.io/flareplot/
		Atlas : https://getcontacts.github.io/atlas/table_user.html 
		To generate a flareplot, a json file is needed. A residue label file is highly recommanded to incorprate to get a clearer view,
		which can map the indentifier in a simpler way. It looks like this:
		cat reslabels.tsv
			A:ASP:254	Protein.ASP254	#666699
			B:ARG:2	Peptide.ARG2	#FF0033
			A:PHE:249	Protein.PHE249	#666699
			A:PHE:262	Protein.PHE262	#666699
			B:ARG:1	Peptide.ARG1	#FF0033
			A:HIS:266	Protein.HIS266	#666699
      	To get this file, run:		
		python geninteraction.py ref.tsv rank.tsv
		By this step, residue label file for both structures will be made, and matched interactions are highlighted in the prediction tsv file.
		And then, we can use the tsv file, residue label file to generate the json file:
		get_contact_flare.py --input contacts.tsv \
			--flarelabels reslabel.tsv \
			--output flareplot.json

		In the json file, optional label are trees and tracks,
		the residue should be group into protein and peptide, which are defiend by preflix in the residue label file.

		[Optional] If you add more than one trees or tracks, then two different plots can be shown, but generally we dont need to make it so complicated.
			"tracks":[
    			{"trackLabel":"reference",
     				"trackProperties":[
       					{"nodeName":"his", "color":"#1500D6", "size":1},
       					...
					]
				},
				{"trackLabel":"model",
					"trackProperties":[
						{"nodeName":"his", "color":"#1500D6", "size":1},
						...
					]
				}
			],
			"trees":[
				{"treeLabel":"reference",
					"treePaths":[
						{"nodeName":"his", "color":"#1500D6", "size":1},
						...
					]
				},
				{"treeLabel":"model",
					"treePath":[
						{"nodeName":"his", "color":"#1500D6", "size":1},
						...
					]
				}
			]

		For visulization in Atlas, we need to upload the tsv file, residue label file and pdb file.
	c. Analysis the interaction popularity 
		for 25 models:
			step1 : get the tsv file for all the 25 models. move them into a folder .
			step2 : generate a csv file
					python countpopular.py Get_interaction/folder, in the folder is all the tsv files of models.
					you will get a csv file, in which contains interaction and their popularities.
		for 1000 models:
			Generate the tsv files for 1000 models: (It takes a bit while)
			python gen_quick_tsv.py aligned_folder
			the output folder will be saved in Get/interaction
			And then, we will calculate Fbur, which is the fraction of interactions of models preserved in crystal structure. 
			However, we will only focus on residues buried in the pocket, and regardless of vdw(~3.5A). To achieve this, specifically inspection 
			of each model and Xtal should be done, and number of residues need to be chosen, then input the range of number we want (a:b),
			only the residue number in this range will be chosen.
			So run this:
			python analyzeInteraction.py ref tsv_folder number_range
			we will get a folder 'Match_inter_1000', in which contains 1000 csv file with annotation YES/NO, indicating whether the models predict the interaction 
			in the xtrl structure correctly. Again, during this step we only count burried residues and non van de wal interaction in.
				
Step 4 : Statistical Analysis
-----------------------------
	a. get the data:
		python analysis.py aligned_folder match_interaction_file
		By this step, a csv file will be generated for each protein in the Analysis_Result folder
		pLDDT, DockQ, GDT, Fbur both for each model will be calculated.
		We use DockQ package to get DockQ score: https://github.com/bjornwallner/DockQ
		GDT score is calculated by LGA program: http://proteinmodel.org/AS2TS/LGA/lga.html download the package from this website
		Here we calculate the GDT score based only on the peptide.

	b. Plotting:
		To get the correlation between scoring function and metrics for each case, run this:
		python genplot.py(need to be improved);

		To make 3D plot:
		python creating3dplot.py

		To compare different method and parameters, first run:
		python plot_stats.py csv_folder
		and will get the plots for comparison among all methods and parameters.(need improved)

		To get the statistics result for the specific method, run:
		python statistic.py csv_folder
		so that we can get the RMSD value for models possessing the best pLDDT value and the best DockQ value. 

generate Decoy 
python MCdecoyspeptides.py -s 6 -r receptor fasta -n 50 -p prefix



summer Project
python generateAlphafold_v2.3.2.py -s GPR37L1_A6NKC4_0.fasta -m 1000 -c 10 -dropout -t 1975-12-01

then massive-screen the models : python Screening_GPR_AFmodel.py model_folder