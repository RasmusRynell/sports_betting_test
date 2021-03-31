
import pandas as pd 
import numpy as np 

from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn. metrics import make_scorer
from sklearn.metrics import f1_score
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import cross_val_predict   

data = pd.read_csv("./final_dataset.csv")
#print(data.head())

pred_this = "result"
drop_this = ["num corners", "num yellow cards", "num free kicks", "num goals", "result"]
drop_this = [x for x in drop_this if x != pred_this]
data.drop(drop_this,1,inplace=True)

#Problem with 2571 (2572 in CSV) contains nun
data = data.drop(labels=2570, axis=0)
print(data.head())
data["result"] = (data["result"] == "H").astype(int)
#data.result = pd.factorize(data.result)[0]
print(data.head())

X_all = data.drop([pred_this],1)
Y_all = data[pred_this]

#print(X_all.head())
#print(Y_all.head())

X_train, X_test, Y_train, Y_test = train_test_split(X_all, Y_all, test_size=50, random_state=2, stratify=Y_all)

clf_SVC = SVC(random_state=912, kernel='rbf', probability=True)
#clf_SVC.fit(X_train, Y_train)
#clf_SVC = DecisionTreeClassifier()
#clf_SVC.fir(X_train, Y_train)




f_scores_test = cross_val_score(clf_SVC, X_all, Y_all, scoring="f1", cv=5)
f_test_error = round(f_scores_test.mean(), 3)
f_test_std = round(f_scores_test.std(), 3)
print("F-score: {} with STD: {}".format(f_test_error, f_test_std))

scores_test = cross_val_score(clf_SVC, X_all, Y_all, cv=5)
test_error = round(scores_test.mean(), 3)
test_std = round(scores_test.std(), 3)
print("Acc: {} with STD: {}".format(test_error, test_std))

