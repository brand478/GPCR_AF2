'''
script to generate plot for anaysis the distribution of top rank, with different metrics.
python plot_stats.py csv_folder
Latest updation: 2023/2/15
Author: Zeyu Cheng, Jens Carlssons lab,Uppsala University
'''
import os
import sys
import csv
import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# Read folder for each method, and combine them into one csv file
def get_stats(method_folder):
  method = method_folder.split('/')[0]
  files = os.listdir(method_folder)

  with open('statistics.csv','a',newline='') as fin:
    writer = csv.writer(fin)

    for csv_file in files: 
        
        ID = csv_file.split('.')[0]
        pdb = ID.split('_')[0]
        csv_file = os.path.join(method_folder, csv_file)
        
        df = pd.read_csv(csv_file)
        
        rank = df['Rank']
        top_rank = rank.idxmin()
        TOP_RMSD = df.loc[top_rank, 'RMSD_B']
        TOP_DockQ= df.loc[top_rank, 'DockQ']
        
        dockq = df['DockQ']
        best_DockQ = dockq.max()

        RMSD_B = df['RMSD_B']
        best_RMSD = RMSD_B.min()
        
        writer.writerow([method, pdb, TOP_RMSD, best_RMSD, TOP_DockQ, best_DockQ])

# Define the method
def BOXPLOT(metrics):
  df = pd.read_csv('statistics.csv')
  df1 = df[df['Method'] == 'AFmulti_v1_25_temp']
  df2 = df[df['Method'] == 'AFmulti_v1_25_notp']
  df3 = df[df['Method'] == 'AFmulti_v1_1000_temp']
  df4 = df[df['Method'] == 'AFmulti_v1_1000_notp']
  df5 = df[df['Method'] == 'AFmulti_v3_1000_default_noTmp']
  df6 = df[df['Method'] == 'AFmulti_v3_1000_dropout_R3_noTmp']
  df7 = df[df['Method'] == 'AFmulti_v3_1000_dropout_R5_noTmp']
  df8 = df[df['Method'] == 'AFmulti_v3_1000_dropout_R7_noTmp']
  df9 = df[df['Method'] == 'AFmulti_v3_1000_dropout_R9_noTmp']

  fig = go.Figure()
  fig.add_trace(go.Violin(y=df1[metrics],x=df1['Method'],box_visible=True, meanline_visible=True))
  fig.add_trace(go.Violin(y=df2[metrics],x=df2['Method'],box_visible=True, meanline_visible=True))
  fig.add_trace(go.Violin(y=df3[metrics],x=df3['Method'],box_visible=True, meanline_visible=True))
  fig.add_trace(go.Violin(y=df4[metrics],x=df4['Method'],box_visible=True, meanline_visible=True))
  fig.add_trace(go.Violin(y=df5[metrics],x=df5['Method'],box_visible=True, meanline_visible=True))
  fig.add_trace(go.Violin(y=df6[metrics],x=df6['Method'],box_visible=True, meanline_visible=True))
  fig.add_trace(go.Violin(y=df7[metrics],x=df7['Method'],box_visible=True, meanline_visible=True))
  fig.add_trace(go.Violin(y=df8[metrics],x=df8['Method'],box_visible=True, meanline_visible=True))
  fig.add_trace(go.Violin(y=df9[metrics],x=df9['Method'],box_visible=True, meanline_visible=True))
  fig.update_traces(quartilemethod="exclusive") # or "inclusive", or "linear" by default
  fig.update_xaxes(tickangle=90)
  fig.update_layout(showlegend=True, yaxis_title=metrics)
  fig.update_traces(meanline_visible=True,
                  points='all', # show all points
                  jitter=0.5,  # add some jitter on points for better visibility
                  scalemode='count') #scale violin plot area with total count
  fig.update_layout(
      autosize=False,
      width=1100,
      height=600,
        
    )
  
  fig.show()

# input = sys.argv[1]
# get_stats(input)
BOXPLOT("Rank1 DockQ")
BOXPLOT("best DockQ")
BOXPLOT("best RMSD")
BOXPLOT("Rank1 RMSD")
# #------------------------------------------------------------------------------------
# group the data by the group column and count the number of values within the range
df = pd.read_csv('statistics.csv')
incorrect = df.groupby('Method')['Rank1 DockQ'].apply(lambda x: ((x < 0.23)).sum())
acceptable = df.groupby('Method')['Rank1 DockQ'].apply(lambda x: ((x >= 0.23) & (x < 0.49)).sum())
medium = df.groupby('Method')['Rank1 DockQ'].apply(lambda x: ((x >= 0.49) & (x < 0.8)).sum())
high = df.groupby('Method')['Rank1 DockQ'].apply(lambda x: (x >= 0.8).sum())

inc_df = {'Method': incorrect.index, 'Rank1 DockQ': incorrect.values}
INC_df= pd.Series(data=inc_df['Rank1 DockQ'], index=inc_df['Method']).reset_index(name='Count')
INC_df = INC_df.rename(columns={'index': 'method'})
INC_df['klass'] = ['incorrect'] * len(INC_df)

acc_df = {'Method': acceptable.index, 'Rank1 DockQ': acceptable.values}
ACC_df= pd.Series(data=acc_df['Rank1 DockQ'], index=acc_df['Method']).reset_index(name='Count')
ACC_df = ACC_df.rename(columns={'index': 'method'})
ACC_df['klass'] = ['acceptable'] * len(ACC_df)

med_df = {'Method': medium.index, 'Rank1 DockQ': medium.values}
MED_df= pd.Series(data=med_df['Rank1 DockQ'], index=med_df['Method']).reset_index(name='Count')
MED_df = MED_df.rename(columns={'index': 'method'})
MED_df['klass'] = ['medium'] * len(MED_df)

high_df = {'Method': high.index, 'Rank1 DockQ': high.values}
HIGH_df= pd.Series(data=high_df['Rank1 DockQ'], index=high_df['Method']).reset_index(name='Count')
HIGH_df = HIGH_df.rename(columns={'index': 'method'})
HIGH_df['klass'] = ['high'] * len(HIGH_df)

combined_df = pd.concat([INC_df, ACC_df, MED_df, HIGH_df], axis=0)


fig = px.bar(combined_df, x="klass", y="Count",
             color="Method", barmode='group',
             title = "Distribution of how many of the total 51 GPCR have first ranked models with incorrect,acceptable,medium and high quality,respectively")
fig.update_layout(xaxis_title='DockQ quality class', yaxis_title='Count')
fig.update_traces(texttemplate='%{y}', textposition='outside')
fig.update_layout(barmode='group')
fig.show()