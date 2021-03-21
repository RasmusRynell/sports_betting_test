
import pandas as pd 
import numpy as np
import xgboost as xgb 

from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC

from sklearn.preprocessing import scale
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import make_scorer
from time import time


data = pd.read_csv("./data/final_dataset.csv")
data.drop(["Unnamed: 0", "HomeTeam", "AwayTeam", "Date", "MW", "HTFormPtsStr", "ATFormPtsStr", \
        "FTHG", "FTAG", "HTGS", "ATGS", "HTGC", "ATGC", "HS", "HTHG", "HTAG", "HTR", "HS", "AS", "HST", "HF", "AF", "HC", "AC", "HY", "AY",
        "HR", "AR"],1, inplace=True)
data.FTR = pd.factorize(data.FTR)[0]
print(data.columns)
print(data.head())
X_all = data.drop(['FTR'],1)
Y_all = data['FTR']

cols = [["HTGD", "ATGD", "HTP", "ATP", "DiffLP"]]
for col in cols:
    X_all[col] = scale(X_all[col])

X_all.HM1 = X_all.HM1.astype("str")
X_all.HM2 = X_all.HM2.astype("str")
X_all.HM3 = X_all.HM3.astype("str")
X_all.AM1 = X_all.AM1.astype("str")
X_all.AM2 = X_all.AM2.astype("str")
X_all.AM3 = X_all.AM3.astype("str")

X_all = X_all[X_all.columns[4:]]
#X_all = X_all.drop(['HTR'],1)
def preprocess_feature(X):
    output = pd.DataFrame(index = X.index)
    
    for col, col_data in X.iteritems():
        if col_data.dtype == object:
            col_data = pd.get_dummies(col_data, prefix=col)
        output = output.join(col_data)
    return output

X_all = preprocess_feature(X_all)

print(X_all.head())

X_train, X_test, Y_train, Y_test = train_test_split(X_all, Y_all, test_size=100, random_state=2, stratify=Y_all)
print("Number of test size: {}".format(len(X_test)))

def train_classifier(clf, X_train, Y_train):
    start = time()
    clf.fit(X_train, Y_train)
    end = time()
    print("Trained model in {:.4f} seconds".format(end-start))

def predict_labels(clf, features, target):
    start = time()
    Y_pred = clf.predict(features)
    end = time()
    print("Made predictions in {:.4f} seconds".format(end-start))
    return f1_score(target, Y_pred, pos_label=0), sum(target == Y_pred) / float(len(Y_pred))

def train_predict(clf, X_train, Y_train, X_test, Y_test):
    print("Training a {} using a training set size of {}. . .".format(clf.__class__.__name__, len(X_train)))
    train_classifier(clf, X_train, Y_train)
    f1, acc = predict_labels(clf, X_train, Y_train)
    print("F1 score and accuracy score for training set: {:.4f}, {:.4f}.".format(f1, acc))

    f1, acc = predict_labels(clf, X_test, Y_test)
    print("F1 score and accuracy score for test set: {:.4f}, {:.4f}.".format(f1, acc))

clf_A = LogisticRegression(random_state=42)
clf_B = SVC(random_state=912, kernel='rbf')
clf_C = xgb.XGBClassifier(seed=82, use_label_encoder=False, eval_metric="error")

train_predict(clf_A, X_train, Y_train, X_test, Y_test)
print()
train_predict(clf_B, X_train, Y_train, X_test, Y_test)
print()
train_predict(clf_C, X_train, Y_train, X_test, Y_test)
print()
