'''
    Members:
        Tran Tan Phong - 18110181
        Vu Thien Nhan - 18110171
    Exercise 2:
    Using train.csv and test.csv
    Perform data dimensionality reduction and feature selection (at least 5 technologies)
    Build model
'''

## IMPORT LIBRARY

import pandas as pd 
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')


# import and create the VarianceThreshold object.
from sklearn.feature_selection import VarianceThreshold

# import the required functions and object.
from sklearn.feature_selection import mutual_info_classif
from sklearn.feature_selection import SelectKBest

# import the required functions and object.
from sklearn.feature_selection import chi2
from sklearn.feature_selection import SelectKBest

# Import train_test_split
from sklearn.model_selection import train_test_split

# Import ML models
from sklearn.ensemble import RandomForestClassifier
from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectFromModel
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import RFE
from sklearn.tree import DecisionTreeClassifier

# Remove outlier function
def remove_outlier(data):
   '''
        Purpose: Remove outlier
        Input: data
        Output: the encoded DataFrame 
   '''
   Q1 = data.quantile(0.25)
   Q3 = data.quantile(0.75)
   IQR = Q3 - Q1
   data_after = data[~((data < (Q1 - 1.5 * IQR)) | (data > (Q3 + 1.5 * IQR))).any(axis=1)]
   print('Shape of data before handling outlier values: ', data.shape)
   print('Shape of data after handling outlier values: ', data_after.shape)
   return data_after   


## FUNCTION TO REMOVE CONSTANT FEATURE USING VARIANCE THRESHOLD

def Constant_Features(X_train, X_test,threshold = 0):
  """
  Removing Constant Features using Variance Threshold
  Input: threshold parameter to identify the variable as constant
         train data (pd.Dataframe) 
         test data (pd.Dataframe)
  Output: train data, test data after applying filter methods
  """
  
  vs_constant = VarianceThreshold(threshold)

  # select the numerical columns only.
  numerical_X_train = X_train[X_train.select_dtypes([np.number]).columns]

  # fit the object to our data.
  vs_constant.fit(numerical_X_train)

  # get the constant colum names.
  constant_columns = [column for column in numerical_X_train.columns
                      if column not in numerical_X_train.columns[vs_constant.get_support()]]

  # detect constant categorical variables.
  constant_cat_columns = [column for column in X_train.columns 
                          if (X_train[column].dtype == "O" and len(X_train[column].unique())  == 1 )]

  # concatenating the two lists.
  all_constant_columns = constant_cat_columns + constant_columns

  # drop the constant columns
  X_train = X_train.drop(labels=all_constant_columns, axis=1, inplace=True)
  X_test = X_test.drop(labels=all_constant_columns, axis=1, inplace=True)
  return X_train, X_test

## 
def Quasi_Constant_Features(X_train, X_test, threshold=0.98):
    """
    Show feature selection using Quasi-Constant
    Input: threshold parameter to identify the variable as constant
         train data (pd.Dataframe) 
         test data (pd.Dataframe)
    Output: train data, test data after applying filter methods
    """
    # create empty list
    quasi_constant_feature = []

    # loop over all the columns
    for feature in X_train.columns:

        # calculate the ratio.
        predominant = (X_train[feature].value_counts() / np.float(len(X_train))).sort_values(ascending=False).values[0]
    
        # append the column name if it is bigger than the threshold
        if predominant >= threshold:
            quasi_constant_feature.append(feature)   
        
    print(quasi_constant_feature)

    # drop the quasi constant columns
    X_train.drop(labels=quasi_constant_feature, axis=1, inplace=True)
    X_test.drop(labels=quasi_constant_feature, axis=1, inplace=True) 
    return X_train, X_test


def Duplicate_Features(X_train, X_test):
    # transpose the feature matrice
    train_features_T = X_train.T

    # print the number of duplicated features
    print(train_features_T.duplicated().sum())

    # select the duplicated features columns names
    duplicated_columns = train_features_T[train_features_T.duplicated()].index.values

    # drop those columns
    X_train.drop(labels=duplicated_columns, axis=1, inplace=True)
    X_test.drop(labels=duplicated_columns, axis=1, inplace=True)
    return X_train, X_test
    

def Correlation_Filter_Methods(X_train, X_test):
    # creating set to hold the correlated features
    corr_features = set()

    # create the correlation matrix (default to pearson)
    corr_matrix = X_train.corr()

    # optional: display a heatmap of the correlation matrix
    plt.figure(figsize=(11,11))
    sns.heatmap(corr_matrix)

    for i in range(len(corr_matrix .columns)):
        for j in range(i):
            if abs(corr_matrix.iloc[i, j]) > 0.8:
                colname = corr_matrix.columns[i]
                corr_features.add(colname)
                
    X_train.drop(labels=corr_features, axis=1, inplace=True)
    X_test.drop(labels=corr_features, axis=1, inplace=True)
    return X_train, X_test


def Mutual_Information(X_train, X_test, y_train, y_test):
    # select the number of features you want to retain.
    select_k = 2

    # get only the numerical features.
    numerical_X_train = X_train[X_train.select_dtypes([np.number]).columns]
    numerical_X_test = X_test[X_test.select_dtypes([np.number]).columns]


    # create the SelectKBest with the mutual info strategy.
    selection = SelectKBest(mutual_info_classif, k=select_k).fit(numerical_X_train, y_train)
    selection = SelectKBest(mutual_info_classif, k=select_k).fit(numerical_X_test, y_test)

    # display the retained features.
    features = X_train.columns[selection.get_support()]
    #print(features)
    return X_train[features], X_test[features]

def Chi_squared_Score(X_train, X_test, y_train, y_test):
    # change this to how much features you want to keep from the top ones.
    select_k = 2

    # apply the chi2 score on the data and target (target should be binary).  
    selection = SelectKBest(chi2, k=select_k).fit(X_train, y_train)

    # display the k selected features.
    features = X_train.columns[selection.get_support()]
    #print(features)
    return X_train[features], X_test[features]

def SelectFromModel(X_train, y_train):
    # define model
    rfc = RandomForestClassifier(n_estimators=100)
    # feature extraction
    select_model = feature_selection.SelectFromModel(rfc)
    # fit on train set
    fit = select_model.fit(X_train, y_train)
    # transform train set
    model_features = fit.transform(X_train)
    return model_features

def PCA_method(X_train, X_test):
    pca = PCA(n_components=2)
    pca.fit(X_train)
    X_train = pca.transform(X_train)
    X_test = pca.transform(X_test)
    return X_train, X_test

def RFE_method(X_train, X_test, y_train, y_test):
#def RFE_method(X_train, y_train):
    # define model
    rfc = RandomForestClassifier(n_estimators=100)
    rfe = RFE(estimator=rfc, n_features_to_select=2)
    # fit the model
    rfe.fit(X_train, y_train)
    # transform the data
    #X_train, y_train = rfe.transform(X_train, y_train)
    #X_test, y_test = rfe.transform(X_test, y_test)
    X_train= rfe.transform(X_train)
    X_test = rfe.transform(X_test)
    #return X_train, y_train, X_test, y_test
    return X_train, X_test

def decision_tree(X_train,y_train,X_test,y_test):
   '''
        Purpose: Use linearSVC to calculate accuracy
        Input: X_train, y_train, X_test, y_test
        Output: accuracy_score
   '''
   clf = DecisionTreeClassifier(random_state= 7)
   clf = clf.fit(X_train, y_train)
   y_pred = clf.predict(X_test)
   return metrics.accuracy_score(y_test, y_pred)


def main():
    #Load Dataset
    path_train='https://raw.githubusercontent.com/pypluf/pypluf.github.Lab_1/\
master/Lab6/Lab6_Dataset/train.csv'
    df_train=pd.read_csv(path_train)

    path_test='https://raw.githubusercontent.com/pypluf/pypluf.github.Lab_1/\
master/Lab6/Lab6_Dataset/test.csv'
    df_test=pd.read_csv(path_test)

    # Show the information of data
    print("\n\n####### 1. LOAD DATASET #######\n\n")
    print("\n\nShow the information of data\n\n")
    print("\n\nPrint the 5 first line of data\n\n")
    print(df_train.head())
    print("\n\nPrint the information of data\n\n")
    print(df_train.info())
    print("\n\nCaculate the sum of null value of data\n\n")
    print(df_train.isna().sum())
    print("\n\nDescribe data\n\n")
    print(df_train.describe())

    ####### 4. DATA CLEANING ####### 
    print("\n\n","~0~0"*27,"\n\n")
    print("\n\n####### 4. DATA CLEANING #######\n\n")

    ## Remove duplicate
    df_train.drop_duplicates(subset = df_train.columns.values[:-1], keep = 'first', inplace = True)
    print("Remove duplicate data: ",df_train.shape)

    df_train.dropna()
    print("Remove missing data: ", df_train.shape)


    ## Remove outlier
    df_train = remove_outlier(df_train)
    print('Remove outlier: ', df_train.shape)

    X_train=df_train.drop(['id','target'],axis=1)
    y_train=df_train['target']
    X_test=df_test.drop(['id'],axis=1)

    ####### 1. APPLY CONSTANT FEATURES #######
    print("\n\n####### 1. APPLY CONSTANT FEATURES  #######\n\n")
    X_train_confea, X_test_confea = Quasi_Constant_Features(X_train, X_test, threshold=0.98)
    print("\n\nShow X_train, X_test after apply Quasi-constant features filter\n\n")
    print("\n\n>>>>>>> X_train after apply Quasi-constant features filter\n\n")
    print(X_train_confea)
    print("\n\n>>>>>>> X_test after apply Quasi-constant features filter\n\n")
    print(X_test_confea)
    '''
    accuracy_decision=decision_tree(X_train_confea ,y_train,X_test_confea,y_test)
    print("Accuracy of Decision Tree: ",accuracy_decision)
    '''

if __name__ == '__main__':
    main()  
