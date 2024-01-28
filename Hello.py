import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pywt

st.header('Welcome the to Wavelet testfield')

# Load the data
#df = pd.read_excel('testData.xlsx')

st.subheader('Start with the data')
st.write('Either upload your own data, which contains a data column and at least one value column, or use the default data set')
# User input for the data file
uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        # Load the data from the uploaded file
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.write("There was an error loading the file: ", e)
else:
    # Load the default data
    df = pd.read_excel('testData.xlsx')
    df=df.iloc[:,1:]


if st.checkbox('Show data?',value=False):
    st.write('This is your data:')
    st.write(df)

st.subheader('Now for some selections')
st.write('Start with selection columns for date/x and value/y')
colsD = st.columns(2)

# User input for the x-axis column
x_col = colsD[0].selectbox('Select column for x-axis (for plotting only)', df.columns,index=0)

# User input for the y-axis column
y_col = colsD[1].selectbox('Select column for y-axis', df.columns,index=1)

st.write(' ')
st.write(' ')
st.write('Then select which wavelets to use')
# User input for the wavelet type
colsW = st.columns(2)
w = colsW[0].selectbox('Select wavelet type 1', ['db1', 'db2', 'db3', 'db4', 'db5', 'db6'],index=0)
w2 = colsW[1].selectbox('Select wavelet type 2', ['db1', 'db2', 'db3', 'db4', 'db5', 'db6'],index=1)

st.write('Select how many decompositionlevels we should use. This can be limited by the number of data points in your data set.')
# User input for the level
lev = st.slider('Select number of decomposition levels', 1, 9,value=3)

# Create llist as a list from 0 to lev
llist = list(range(lev+1))

# Ask the user which numbers should be left out
st.write("Uncheck the levels to be left out. Genereally seen, if higher numbers are unchecked, the funtion can work as a noise filter. If lower numbers are unchecked we instead remove slow trends.")
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
st.write(' ')
st.write(' ')
st.subheader('Plotting')
st.write('Select between which years the plotting will occure. This is only for the plotting, does not effect the tranformations and is there so the plotting range will be kept even if the user inputs above are changed.')
date_range_year = st.slider('Select date range', min_value=min_date_year, max_value=max_date_year, value=(min_date_year, max_date_year))

coeffs = pywt.wavedec(dd, w, level=lev)
coeffs2 = pywt.wavedec(dd, w2, level=lev)

for i in llist:
    coeffs[i] = coeffs[i]*0
    coeffs2[i] = coeffs2[i]*0

a = pywt.waverec(coeffs,w)
a2 = pywt.waverec(coeffs2,w2)

a=a[0:df.shape[0]]
a2=a2[0:df.shape[0]]

# add the result to the data frame
df.loc[:,w]=a
df.loc[:,w2]=a2

pumpWT = a.copy()

# Create a figure
fig = go.Figure()
# Add first line
fig.add_trace(go.Scatter(x=t, y=dd, mode='lines', name='Original data'))
# Add second line
fig.add_trace(go.Scatter(x=t, y=a[0:], mode='lines', name=w))
# Add third line
fig.add_trace(go.Scatter(x=t, y=a2[0:], mode='lines', name=w2))
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
y_min = min([df_filtered[y_col].min(),df_filtered.loc[:,w].min(),df_filtered.loc[:,w2].min()])
y_max = max([df_filtered[y_col].max(),df_filtered.loc[:,w].max(),df_filtered.loc[:,w2].max()])

# Add 10% of the range to each side
y_range = y_max - y_min
y_min -= y_range * 0.1
y_max += y_range * 0.1


# Update y-axis range
fig.update_yaxes(range=[y_min, y_max])

# Show the figure
st.plotly_chart(fig)

#st.write(y_max)

# Convert the transformed data to an Excel file
df=df.drop([x_col + '_year'],axis=1)

df.to_excel('dataWL.xlsx', index=False)
# Add download buttons for the Excel files
st.download_button(
    label="Download transformed data",
    data=pd.read_excel("dataWL.xlsx").to_csv(index=False).encode(),
    file_name="dataWL.csv",
    mime="text/csv",
)
st.write('This is the data you will download:')
st.write(df)
