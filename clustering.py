#!/usr/bin/env python
# coding: utf-8

# In[2]:


from sklearn.cluster import KMeans
from kneed import KneeLocator
import matplotlib.pyplot as plt
import pickle 
import os
import shutil

class modelOperation:
    
    def __init__(self):
        model_dir='model/'
        
    def save_model(model,filename):
        path = os.path.join(model_dir,filename)  #create seperate directory for each cluster
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


class KMeansClustering:
    
    def elbow_plot(data):
        ss=[]
        
        for i in range(1,11):
            kmeans=KMeans(n_clusters=i,init='k-means++',random_state=7)
            kmeans.fit(data)
            ss.append(kmeans.inertia_)
            
        plt.plot(range(1,11),ss) # creating the graph between SS and the number of clusters
        plt.title('The Elbow Method')
        plt.xlabel('Number of clusters')
        plt.ylabel('SS')
        
        plt.savefig('K-Means_Elbow.PNG')
        
        kn = KneeLocator(range(1, 11), ss, curve='convex', direction='decreasing') #Xaxis,Yaxis,curveshape,direction
        
        return kn.knee
    
    
    def create_cluster(data,number_of_clusters):
        kmeans = KMeans(n_clusters=number_of_clusters, init='k-means++', random_state=7)
        
        y_kmeans = kmeans.fit_predict(data)  #divide data into clusters
        save_model = modelOperation.save_model(kmeans, 'KMeans')
        
        data['Cluster']=y_kmeans  # create a new column in dataset for storing the cluster information
        return data


# In[ ]:





# In[ ]:




