import json

import models.pred_LDA_SVC as pred_LDA_SVC
import models.pred_SVC as pred_SVC
import models.pred_decision_tree as decision_tree


def eval_models(file, pred_this, gamePk):
    print("Pred LDA SVC:")
    pred = pred_LDA_SVC.pred(file, pred_this, gamePk)
    print(pred)


print("Alexander Ovechkin")
eval_models("./data/pp_alexander_ovechkin.csv", 3.5, 2020020692)
print()
"""
print("Jack Hughes")
eval_models("./data/pp_2020020151_jack_hughes.csv", 1.5, 2020020556)
print()
"""