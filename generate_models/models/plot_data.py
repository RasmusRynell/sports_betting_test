import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.manifold import TSNE
from sklearn.model_selection import train_test_split

from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier

from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import cross_val_score


data = pd.read_csv("./data/td/pp_duncan_keith.csv")
data = data.replace(np.nan, 0)
pred_this = "shots_this_game_O2.5"

drop_this = ["shots_this_game_total", "shots_this_game_O1.5", "shots_this_game_U1.5", "shots_this_game_O2.5", "shots_this_game_U2.5", "shots_this_game_O3.5", "shots_this_game_U3.5", "shots_this_game_O4.5", "shots_this_game_U4.5","date"]

drop_this = [x for x in drop_this if x != pred_this]
data.drop(drop_this,1, inplace=True)

x = data.drop([pred_this],1)
y = data[pred_this]
"""
x = StandardScaler().fit_transform(x)

#pca = PCA(n_components=2)
pca = TSNE(n_components=2)

principalComponents = pca.fit_transform(x)
principalDf = pd.DataFrame(data = principalComponents
             , columns = ['principal component 1', 'principal component 2'])

finalDf = pd.concat([principalDf, data[[pred_this]]], axis = 1)  

fig = plt.figure(figsize = (8,8))
ax = fig.add_subplot(1,1,1) 
ax.set_xlabel('Principal Component 1', fontsize = 15)
ax.set_ylabel('Principal Component 2', fontsize = 15)
ax.set_title('2 component PCA', fontsize = 20)
targets = [0, 1]
colors = ['r', 'g']
for target, color in zip(targets,colors):
    indicesToKeep = finalDf[pred_this] == target
    ax.scatter(finalDf.loc[indicesToKeep, 'principal component 1']
               , finalDf.loc[indicesToKeep, 'principal component 2']
               , c = color
               , s = 50)
ax.legend(targets)
ax.grid()

plt.show()
"""


X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=0)
sc = StandardScaler()
X_train = sc.fit_transform(X_train)
X_test = sc.transform(X_test)
#pca = PCA(n_components=50)
#X_train = pca.fit_transform(X_train)
#X_test = pca.transform(X_test)
#classifier = RandomForestClassifier(max_depth=2, random_state=0, class_weight="balanced")
#classifier = KNeighborsClassifier(n_neighbors=10)
classifier = SVC(class_weight="balanced")
classifier.fit(X_train, y_train)

model = SVC()
param_grid = [
    {'C': [1, 10, 100, 1000], 'kernel': ['linear']},
    {'C': [1, 10, 100, 1000], 'gamma': [0.001, 0.0001], 'kernel': ['rbf']},
]
rand_search = GridSearchCV(estimator=model, param_grid=param_grid, cv=5, n_jobs=-1, scoring="roc_auc")
pipeline = make_pipeline(StandardScaler(), rand_search)
score_acc = round(cross_val_score(pipeline, x, y, cv=5, n_jobs=-1, scoring="precision").mean(), 3)
print(score_acc)
score_acc = round(cross_val_score(pipeline, x, y, cv=5, n_jobs=-1, scoring="recall").mean(), 3)
print(score_acc)
svc_model = pipeline.fit(X_train, y_train)
scaler = StandardScaler()
X_all_scaled = scaler.fit_transform(X_train)

pred = svc_model.predict(scaler.transform(X_test))
matrix = confusion_matrix(y_test, pred)
print(matrix)

# Predicting the Test set results
y_pred = classifier.predict(X_test)
cm = confusion_matrix(y_test, y_pred)
print(cm)
print('Accuracy: ' + str(accuracy_score(y_test, y_pred)))
