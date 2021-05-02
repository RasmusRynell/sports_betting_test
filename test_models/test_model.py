import argh
import json
from tqdm import tqdm
from unidecode import unidecode

from handler import api

#Import all models
import models.models.pred_SVC as pred_SVC
import models.models.pred_SVC_opt as pred_SVC_opt
import models.models.pred_logistic_regression as pred_logistic_regression
import models.models.pred_KNN as pred_KNN

# Fixa mina modeller med "pipe" och korrekt skalning https://scikit-learn.org/stable/modules/preprocessing.html
# Bra post, https://stackoverflow.com/questions/38077190/how-to-increase-the-model-accuracy-of-logistic-regression-in-scikit-python 
# Tror jag har missat att skala om datan för slutgiltiga prediction
f = open

