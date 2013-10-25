import data_io

def predict():
    # Get parameters + call estimate
    pass

def estimate(features):
    print("[INFO] Loading the classifier")
    classifier = data_io.load_model()

    print("[INFO] Making predictions")
    predictions = classifier.predict_proba(features)
    
    return predictions
    
if __name__=="__main__":
    estimate()
