import sys
import data_io

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.gaussian_process import GaussianProcess
from sklearn.datasets import load_svmlight_file

train = None
features = None
target = None

def Load_data_csv():
    print("[INFO] Loading data format data...")
    global train

    train = data_io.read_train_csv()
    train.fillna(0, inplace=True)
    train_sample = train.fillna(value=0)
    feature_names = list(train_sample.columns)
    
    feature_names.remove("label")
    
    global features
    global target

    features = train_sample[feature_names].values
    target = train_sample["label"].values
    
    target = train_sample["booking_bool"].values

def Load_data_svm():
    print("[INFO] Loading svm-light format data...")
    global features
    global target
    features, target = load_svmlight_file(data_io.read_train_svm())
    features = features.todense()

def Random_Forest_Classifier():
    print("===== RandomForest =====")
    print("[INFO] Training the Classifier")
    #classifier = RandomForestClassifier(n_estimators=100, verbose=2, n_jobs=4, min_samples_split=10, random_state=1)
    classifier = RandomForestClassifier(n_estimators=1000, verbose=2, n_jobs=5, max_depth=10, min_samples_split=10, max_features=9, random_state=1, criterion='gini', compute_importances='True')
    classifier.fit(features, target)
    
    print("Saving the classifier")
    data_io.save_model(classifier)

def Logistic_Regression_Classifier():
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

if __name__=="__main__":
    Load_data_csv()
    #Load_data_svm()
    #RandomForest()
    #LogisticRegressionClassifier()
    GradientBoosting()
