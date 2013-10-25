import data_io

def estimate(features, target):
    print("[INFO] Loading the classifier")
    classifier = data_io.load_model()

    print("[INFO] Making predictions")
    predictions = classifier.predict_proba(features)
    
    return predictions
    
if __name__=="__main__":
    estimate()
