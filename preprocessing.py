#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
from sklearn.impute import KNNImputer
from sklearn.preprocessing import StandardScaler

class preprocessor:
    
    
    def remove_columns(data,columns):
        # taking dataframe and name of columns to be removed
        
        useful_data=data.drop(labels=columns,axis=1)
        
        return useful_data
    
    def separate_label_feature(data,label_column_name):
        #taking dataframe and label col name or output col name
        X = data.drop(labels=label_column_name,axis=1)
        Y = data[label_column_name] #take the output col in Y
        
        return X,Y
    
    def dropUnnecessaryCol(data,columnList):
        data = data.drop(columnList,axis=1)
        return data
    
    def standardScaling(X):
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        return X_scaled


# In[ ]:




