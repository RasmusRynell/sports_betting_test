
from sklearn.model_selection import cross_val_score
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import make_scorer, accuracy_score, precision_score


def eval_model(pipeline, X_all, Y_all, earliest_gamePk_index, pred_this):

    score_acc = round(cross_val_score(pipeline, X_all, Y_all, cv=5, n_jobs=-1, scoring="accuracy").mean(), 3)
    scorer = make_scorer(precision_score, zero_division=0.0)
    score_precision = round(cross_val_score(pipeline, X_all, Y_all, cv=5, n_jobs=-1, scoring=scorer).mean(), 3)

    X_train, X_test, y_train, y_test = train_test_split(X_all, Y_all, test_size=0.33, random_state=42)
    svc_model = pipeline.fit(X_train, y_train)
    pred = svc_model.predict(X_test)
    matrix = confusion_matrix(y_test, pred)

    return {"confusion matrix": matrix, "accuracy": score_acc, "precision accuracy": score_precision}

def print_eval(eval_model, model_name):
    print("--------------------------------------------------")
    print("Model used: {}".format(model_name))
    print("Confusion matrix:\n {}".format(eval_model["confusion matrix"]))
    print("Accuracy: {}\tPrecision accuracy: {}"\
        .format(eval_model["accuracy"], eval_model["precision accuracy"]))
    print("--------------------------------------------------")
