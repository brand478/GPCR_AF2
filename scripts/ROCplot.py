'''
script for enrichment plot
'''

import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_curve, roc_auc_score
import matplotlib.pyplot as plt


df = pd.read_csv('AF2_enrichment/gpr139_enriching_fix.csv')

true_labels = df['activity'].values
confidence_score = df['confidence score'].values
pDockQ_score = df['pDockQ'].values


fpr_1, tpr_1, thresholds_1 = roc_curve(true_labels, confidence_score)
auc_score_1 = roc_auc_score(true_labels, confidence_score)
fpr_2, tpr_2, thresholds_2 = roc_curve(true_labels, pDockQ_score)
auc_score_2 = roc_auc_score(true_labels, pDockQ_score)


# Create an empty figure, and iteratively add new lines
# every time we compute a new class
fig = go.Figure()
fig.add_shape(
    type='line', line=dict(dash='dash'),
    x0=0, x1=1, y0=0, y1=1
)

name_1 = f"confidence score (AUC={auc_score_1:.2f})"
name_2 = f"pDockQ score (AUC={auc_score_2:.2f})"

fig.add_trace(go.Scatter(x=fpr_1, y=tpr_1, name=name_1, mode='lines'))
fig.add_trace(go.Scatter(x=fpr_2, y=tpr_2, name=name_2, mode='lines'))


fig.update_layout(
    xaxis_title='False Positive Rate',
    yaxis_title='True Positive Rate',
    yaxis=dict(scaleanchor="x", scaleratio=1),
    xaxis=dict(constrain='domain'),
    width=700, height=500
)
fig.show()   


# plt.plot(fpr_2,tpr_2, label = 'ROC curve (area=%0.2f)' % auc_score_2)
# plt.plot([0,1], [0,1], 'k--')
# plt.xlim([0.0,1.0])
# plt.ylim([0.0,1.05])
# plt.xlabel('False positive rate')
# plt.ylabel('Ture positive rate')
# plt.legend(loc = 'lower right')
# plt.savefig('roc_curve.png')