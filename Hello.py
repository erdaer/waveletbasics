import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pywt

# Load the data
df = pd.read_excel('testData.xlsx')

colsD = st.columns(2)

# User input for the x-axis column
x_col = colsD[0].selectbox('Select column for x-axis (for plotting only)', df.columns)

# User input for the y-axis column
y_col = colsD[1].selectbox('Select column for y-axis', df.columns)

# User input for the wavelet type
colsW = st.columns(2)
w = colsW[0].selectbox('Select wavelet type 1', ['db1', 'db2', 'db3', 'db4', 'db5', 'db6'],index=0)
w2 = colsW[1].selectbox('Select wavelet type 2', ['db1', 'db2', 'db3', 'db4', 'db5', 'db6'],index=1)

# User input for the level
lev = st.slider('Select level', 1, 9)

# Create llist as a list from 0 to lev
llist = list(range(lev+1))

# Ask the user which numbers should be left out
st.write("Uncheck the numbers to be left out:")
left_out = []
cols = st.columns(lev+1)
#st.write(cols[0])
for i in llist:
    if cols[i].checkbox(str(i), value=True):
        left_out.append(i)

# Remove the selected numbers from llist
llist = [i for i in llist if i not in left_out]

# Wavelet analysis 
dd = df.loc[:,y_col]
t = df.loc[:,x_col]

# Convert the dates to year with one decimal
df[x_col + '_year'] = df[x_col].dt.year + df[x_col].dt.month / 12.0

# Get the min and max dates as year with one decimal
min_date_year = df[x_col + '_year'].min()
max_date_year = df[x_col + '_year'].max()

# User input for the date range (as year with one decimal)
date_range_year = st.slider('Select date range', min_value=min_date_year, max_value=max_date_year, value=(min_date_year, max_date_year))

coeffs = pywt.wavedec(dd, w, level=lev)
coeffs2 = pywt.wavedec(dd, w2, level=lev)

for i in llist:
    coeffs[i] = coeffs[i]*0
    coeffs2[i] = coeffs2[i]*0

a = pywt.waverec(coeffs,w)
a2 = pywt.waverec(coeffs2,w2)

pumpWT = a.copy()

# Create a figure
fig = go.Figure()
# Add first line
fig.add_trace(go.Scatter(x=t, y=dd, mode='lines', name='Line 1'))
# Add second line
fig.add_trace(go.Scatter(x=t, y=a[0:], mode='lines', name='Line 2'))
# Add third line
fig.add_trace(go.Scatter(x=t, y=a2[0:], mode='lines', name='Line 3'))
# Update x-axis range
#fig.update_xaxes(range=[pd.to_datetime(date_range_year[0], format='%Y.%m'), pd.to_datetime(date_range_year[1], format='%Y.%m')])
# Specify the size of the figure
fig.update_layout(
    autosize=False,
    width=1200,  # Width of the figure in pixels
    height=600,  # Height of the figure in pixels
    margin=dict(l=50, r=50, b=100, t=100, pad=4),
    paper_bgcolor="white",
)

from datetime import timedelta

# Convert the selected range from year with one decimal to datetime
start_year = int(date_range_year[0])
start_days = int((date_range_year[0] - start_year) * 365)
start_date = pd.Timestamp(year=start_year, month=1, day=1) + timedelta(days=start_days)

end_year = int(date_range_year[1])
end_days = int((date_range_year[1] - end_year) * 365)
end_date = pd.Timestamp(year=end_year, month=1, day=1) + timedelta(days=end_days)

# Update x-axis range
fig.update_xaxes(range=[start_date, end_date])

# Filter the dataframe based on the selected date range
df_filtered = df[(df[x_col + '_year'] >= date_range_year[0]) & (df[x_col + '_year'] <= date_range_year[1])]

# Calculate the range of y values in the filtered dataframe
y_min = df_filtered[y_col].min()
y_max = df_filtered[y_col].max()

# Add 10% of the range to each side
y_range = y_max - y_min
y_min -= y_range * 0.1
y_max += y_range * 0.1


# Update y-axis range
fig.update_yaxes(range=[y_min, y_max])

# Show the figure
st.plotly_chart(fig)

#st.write(y_max)
