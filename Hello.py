import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
#from sklearn.preprocessing import StandardScaler
import pywt

# Load the data
df = pd.read_excel('testData.xlsx')

# User input for the wavelet type
w = st.selectbox('Select wavelet type', ['db1', 'db2', 'db3', 'db4', 'db5', 'db6'])

# Wavelet analysis 
dd = df.iloc[:,-1]
t = df.Datum

lev = 9
coeffs = pywt.wavedec(dd, w, level=lev)

llist = [0,1,2,3,4,5,8,9]
for i in llist:
    coeffs[i] = coeffs[i]*0

a = pywt.waverec(coeffs,w)

pumpWT = a.copy()

# Create a figure
fig = go.Figure()
# Add first line
fig.add_trace(go.Scatter(x=t, y=dd, mode='lines', name='Line 1'))
# Add second line
fig.add_trace(go.Scatter(x=t, y=a[0:], mode='lines', name='Line 2'))
# Specify the size of the figure
fig.update_layout(
    autosize=False,
    width=1200,  # Width of the figure in pixels
    height=600,  # Height of the figure in pixels
    margin=dict(l=50, r=50, b=100, t=100, pad=4),
    paper_bgcolor="white",
)

# Show the figure
st.plotly_chart(fig)
