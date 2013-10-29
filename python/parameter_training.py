import sys
import data_io

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.gaussian_process import GaussianProcess


train = None
features = None
target = None


def Random_Forest_Classifier(features, target):
    print("===== RandomForest =====")
    print("[INFO] Training the Classifier")
    max_f = min(9, len(features[0]))
    # TODO(nkhadke, senwu): Figure out multiprocessing error
    classifier = RandomForestClassifier(n_estimators=1000, verbose=2, n_jobs=1, max_depth=10, min_samples_split=10, max_features=max_f, random_state=1, criterion='gini', compute_importances='True')
    classifier.fit(features, target)
    
    print("Saving the classifier")
    data_io.save_model(classifier)

def Logistic_Regression_Classifier(features, target):
    print("===== LogisticRegression =====")
    print("[INFO] Training the Classifier")
    classifier = LogisticRegression(penalty='l1', dual=False, tol=0.000001, C=0.1, fit_intercept=True, intercept_scaling=1, class_weight=None, random_state=1)
    classifier.fit(features, target)

    print("Saving the classifier")
    data_io.save_model(classifier)

def Gradient_Boosting_Classifier(features, target):
    print("===== GradientBoosting =====")
    print("[INFO] Training the Classifier")
    classifier = GradientBoostingClassifier(learning_rate=0.1,n_estimators=50,max_depth=5,verbose=2,min_samples_split=10,max_features=9,random_state=1)
    classifier.fit(features, target)

    print("Saving the classifier")
    data_io.save_model(classifier)


def Gaussian_Process_Regression(features, target):
    print("===== GaussianProcess =====")
    print("[INFO] Training the Classifier")
    
    classifier = GaussianProcess(theta0=0.1, thetaL=0.001, thetaU=1.0)
    classifier.fit(features, target)
    
    print("Saving the classifier")
    data_io.save_model(classifier)

def train(features, target):
    Random_Forest_Classifier(features, target)
    #Logistic_Regression_Classifier(features, target)
    #Gradient_Boosting_Classifier(features, target)
    #Gaussian_Process_Regression(features, target)

if __name__=="__main__":
    pass
