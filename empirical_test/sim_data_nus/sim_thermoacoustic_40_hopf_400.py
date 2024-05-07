import pandas as pd
import numpy as np
import ewstools
import os

# Get the absolute path of the current file
current_file_path = os.path.abspath(__file__)

# Get the directory containing the current file
current_dir = os.path.dirname(current_file_path)

# Change the working directory to the directory of the current file
os.chdir(current_dir)

series_len = 400
numSims = 4
# EWS parameters
dt2 = 1 # spacing between time-series for EWS computation
rw = 0.25 # rolling window
span = 0.2 # bandwidth
lags = [1] # autocorrelation lag times
ews = ['var','ac']

txt = open('../empirical_data/thermoacoustic_40mv.txt')
datalines = txt.readlines()
dataset = []
for data in datalines:
    data = data.strip().split()
    dataset.append(data)

for data in dataset:
    data[0] = (float(data[0])-3.65629963087196300E+9)*0.04
    data[1] = float(data[1])*1000/0.2175

dataset_1 = dataset[:int(6E5/(2.4/1))] # 0-1
dataset_2 = dataset[int(6E5/(2.4/0.05)):int(6E5/(2.4/1.05))] # 0.05-1.05
dataset_3 = dataset[int(6E5/(2.4/0.1)):int(6E5/(2.4/1.1))]   # 0.1-1.1
dataset_4 = dataset[int(6E5/(2.4/0.15)):int(6E5/(2.4/1.15))] # 0.15-1.15

dataset_sum = [dataset_1,dataset_2,dataset_3,dataset_4]
par_range_sum = ['0-1','0.05-1.05','0.1-1.1','0.15-1.15']
appended_ews = []

for c in range(numSims):

    dataset = np.array(dataset_sum[c])

    d = np.arange(0,len(dataset))
    np.random.shuffle(d)
    d = list(np.sort(d[0:series_len]))
    dataset_dl = dataset[d]

    df_mic = pd.DataFrame(data=None,columns=['x','b'])
    df_mic['x'] = dataset_dl[:,1]
    df_mic['b'] = dataset_dl[:,0]

    ews_dic = ewstools.core.ews_compute(df_mic['x'], 
                roll_window = rw,
                smooth='Lowess',
                span = span,
                lag_times = lags, 
                ews = ews)
    
    # The DataFrame of EWS
    df_ews_temp = ews_dic['EWS metrics']
    # Include a column in the DataFrames for realisation number and variable
    df_ews_temp['tsid'] = c+1
    df_ews_temp['b'] = df_mic['b']
        
    # Add DataFrames to list
    appended_ews.append(df_ews_temp)

    print('EWS for realisation '+str(c+1)+' complete')

# Concatenate EWS DataFrames
df_ews = pd.concat(appended_ews).reset_index()

#------------------------------------
# Export data 
#-----------------------------------

# Create directories for output
if not os.path.exists('../data_nus'):
    os.makedirs('../data_nus')

if not os.path.exists('../data_nus/thermoacoustic_hopf'):
    os.makedirs('../data_nus/thermoacoustic_hopf')

for i in np.arange(numSims)+1:
    df_resids = df_ews[df_ews['tsid'] == i][['Time','Residuals','b']]
    filepath_resids='../data_nus/thermoacoustic_hopf/thermoacoustic_40_hopf_400_resids_{}.csv'.format(par_range_sum[i-1])
    df_resids.to_csv(filepath_resids,index=False)