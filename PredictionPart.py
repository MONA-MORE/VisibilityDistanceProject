#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
from preprocessing import preprocessor


# In[2]:


import sqlite3
from datetime import datetime
from os import listdir
import os
import re
import json
import shutil
import pandas as pd


# ## Prediction batch files validation

# In[3]:


class Prediction_Data_validation:
    
    def __init__(path):
        Batch_Directory = path
        schema_path = 'schema_prediction.json'
    def valuesFromSchema():
        # it will extract all the information from given schema
        f = open(schema_path,'r')
        dict1 = json.load(f)  # it will return json object containing data in key-value pairs
        f.close()
        #print(type(dict1))
        pattern = dict1['SampleFileName']
        LengthOfDateStampInFile = dict1['LengthOfDateStampInFile']
        LengthOfTimeStampInFile = dict1['LengthOfTimeStampInFile']
        column_names = dict1['ColName']
        NumberofColumns = dict1['NumberofColumns']
        
        return LengthOfDateStampInFile, LengthOfTimeStampInFile, column_names, NumberofColumns
    
    def FileNameRegex():
        #regular exp for the filename from training batch files
        regex = "['visibility']+['\_'']+[\d_]+[\d]+\.csv"
        return regex
    def validationFileName(regex,LengthOfDateStampInFile,LengthOfTimeStampInFile):
        # file name validation with regex and schema info
        
        onlyfiles = [f for f in listdir(Batch_Directory)] # this will give all the files at given path
        #destination="Prediction_files_validated/Good_data"
        #destination2="Prediction_files_validated/Bad_data"
        for filename in onlyfiles:
                if (re.match(regex, filename)):
                    split1 = re.split('.csv', filename)
                    split2 = (re.split('_', split1[0]))
                    if len(split2[1]) == LengthOfDateStampInFile:
                        
                        if len(split2[2]) == LengthOfTimeStampInFile:
                            shutil.copy("Prediction_Batch_Files/" + filename, "Prediction_files_validated/Good_data")
                        else:
                            shutil.copy("Prediction_Batch_Files/" + filename, "Prediction_files_validated/Bad_data")
                    else:
                        shutil.copy("Prediction_Batch_Files/" + filename, "Prediction_files_validated/Bad_data")
                else:
                    shutil.copy("Prediction_Batch_Files/" + filename, "Prediction_files_validated/Bad_data")
        
    def validateColumnLength(NumberofColumns):
        # even if file name is right ,it may happen that no. of cols are not same
        # so this function will validate that.
        
        for file in listdir('Prediction_files_validated/Good_data/'):
            csv = pd.read_csv("Prediction_files_validated/Good_data/" + file)
            if csv.shape[1] == NumberofColumns:  #shape gives(rows,columns) so index 1
                pass
            else:
                shutil.move("Prediction_files_validated/Good_data/" + file, "Prediction_files_validated/Bad_data")
                
    def deletePredictionFile():

        if os.path.exists('Prediction_Output_File/Predictions.csv'):
            os.remove('Prediction_Output_File/Predictions.csv')
            


# ## Database operations

# In[4]:


import csv


# In[7]:


class dBOperation:           #This class is used for handling all the SQL operations.
    
    path = "Prediction_Database/"
    badFilePath = "Training_files_validated/Bad_data"
    goodFilePath = "Training_files_validated/Good_data"
    
    def dataBaseConnection(DatabaseName):
        # This method creates the database with the given name and 
        # if Database already exists then opens the connection to the DB.
        
        conn = sqlite3.connect(path+DatabaseName+'.db')
        return conn
    
    def createTableDb(DatabaseName,column_names):
        
    #This method creates a table in the given database which will be used to insert the Good data
        conn = dataBaseConnection(DatabaseName)
        for key in column_names.keys():
            type = column_names[key]
            try:
                conn.execute('ALTER TABLE Good_Raw_Data ADD COLUMN "{column_name}" {dataType}'.format(column_name=key,dataType=type))
            except:
                
                conn.execute('CREATE TABLE  Good_Raw_Data ({column_name} {dataType})'.format(column_name=key, dataType=type))
        conn.close()
        
    def insertIntoTableGoodData(Database):
        conn = dataBaseConnection(Database)
        goodFilePath= goodFilePath
        badFilePath = badFilePath
        onlyfiles = [f for f in listdir(goodFilePath)]
        
        for file in onlyfiles:
            
            with open(goodFilePath+'/'+file, "r") as f:
                next(f)
                reader = csv.reader(f, delimiter="\n")
                for line in enumerate(reader):
                    for list_ in (line[1]):
                        conn.execute('INSERT INTO Good_Raw_Data values ({values})'.format(values=(list_)))
                        conn.commit()
                

        conn.close()
        
        
            
    def selectingDatafromtableintocsv(Database):
        #This method exports the data from Good_Raw_Data table as a CSV file. at a given location.
        
        
        fileName = 'InputFile1.csv'
        conn = dataBaseConnection(Database)
        sqlSelect = "SELECT *  FROM Good_Raw_Data"
        cursor = conn.cursor()

        cursor.execute(sqlSelect)
        results = cursor.fetchall()
        
        # Get the headers of the csv file
        headers = [i[0] for i in cursor.description]  #description property will return a list of tuples describing the columns
        # 0th index is always a col name in description 
        with open( fileName, 'w', newline='') as csvFile:
            csvFile = csv.writer(csvFile,delimiter=',',lineterminator='\n')
        
            csvFile.writerow(headers)   # for single row at a time--to write the field names or col names
            csvFile.writerows(results)  # for multiple rows at a time
        


# In[ ]:





# In[8]:


class pred_validation:
    def __init__(path):
        raw_data = Prediction_Data_validation(path)
        dBOperation = dBOperation()
        
    def prediction_validation():
        
            # extracting values from prediction schema
            LengthOfDateStampInFile, LengthOfTimeStampInFile, column_names, noofcolumns = raw_data.valuesFromSchema()
            # getting the regex defined to validate filename
            regex = raw_data.FileNameRegex()
            # validating filename of prediction files
            raw_data.validationFileName(regex, LengthOfDateStampInFile, LengthOfTimeStampInFile)
            # validating column length in the file
            raw_data.validateColumnLength(noofcolumns)
            
           
            # create database with given name, if present open the connection! Create table with columns given in schema
            dBOperation.createTableDb('Training', column_names)
           
            # insert csv files in the table
            dBOperation.insertIntoTableGoodData('Training')
            

            # export data in table to csvfile
            dBOperation.selectingDatafromtableintocsv('Training')
            


# In[ ]:





# In[9]:


import pickle 
import os
import shutil

class modelOperation:
    
    model_dir = "D:/cdac/CDAC_PROJECT/Untitled Folder/model"
    
    def save_model(model,filename):
        path = os.path.join("D:/cdac/CDAC_PROJECT/Untitled Folder/model",filename)  #create seperate directory for each cluster
        if os.path.isdir(path):   #remove previously existing models for each clusters
            shutil.rmtree(model_dir)
            os.makedirs(path)
        else:
            os.makedirs(path) 
            with open(path +'/' + filename+'.sav','wb') as f:
                
                pickle.dump(model, f)
        return 'success'
    
    def load_model(filename):
        with open(model_dir + filename + '/' + filename + '.sav','rb') as f:
            return pickle.load(f)
        
    def find_correct_model_file(cluster_number):
        
        cluster_number= cluster_number
        folder_name= model_dir
        list_of_model_files = []
        list_of_files = os.listdir(folder_name)
        for file in list_of_files:
            try:
                if (file.index(str(cluster_number))!=-1):
                    model_name=file
            except:
                continue
        model_name=model_name.split('.')[0]
        return model_name
        


# In[10]:


class prediction:
    def __init__(path):
        pred_data_val = Prediction_Data_validation(path)
    
    def predictionFromModel():
        data = preprocessor.dropUnnecessaryCol(data,['DATE','Precip','WETBULBTEMPF','DewPointTempF','StationPressure'])
        
        kmeans=modelOperation.load_model('KMeans')
        
        clusters=kmeans.predict(data)#drops the first column for cluster prediction
        data['clusters']=clusters
        clusters=data['clusters'].unique()
        result=[] # initialize blank list for storing predicitons
        
        for i in clusters:
            cluster_data= data[data['clusters']==i]
            cluster_data = cluster_data.drop(['clusters'],axis=1)
            model_name = modelOperation.find_correct_model_file(i)
            model = modelOperation.load_model(model_name)
            for val in (model.predict(cluster_data.values)):
                result.append(val)
            
        result = pandas.DataFrame(result,columns=['Predictions'])
        path="Prediction_Output_File/Predictions.csv"
        result.to_csv("Prediction_Output_File/Predictions.csv",header=True) #appends result to prediction file
        
        return path
    
        
        
        
        


# In[ ]:




