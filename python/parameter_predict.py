import data_io
import random

from sklearn.datasets import load_svmlight_file

prime = []
candidate = []

def search(base, coun, x, y):
    if (x >= len(base)):
        global candidate
        candidate.append(y)
        return
    for i in range(0, coun[x] + 1):
        search(base, coun, x + 1, y * (base[x] ** i))

def gen_candidate(x):
    base = []
    coun = []
    global prime
    for i in range(len(prime)):
        if (prime[i] > x):
            break
        if ((x / prime[i]) * prime[i] == x):
            base.append(prime[i])
            coun.append(0)
            while ((x / prime[i]) * prime[i] == x):
                coun[len(coun) - 1] += 1
                x /= prime[i]
    search(base, coun, 0, 1)


def gen_prime(x):
    ret = []
    b = []
    for i in range(int(x) + 1):
        b.append(True)
    b[0] = False
    b[1] = False
    for i in range(int(x) + 1):
        if (b[i] == True):
            ret.append(i)
            j = 2
            while (j * i <= x):
                b[j * i] = False
                j += 1
    return ret


def estimate():

    features, target = load_svmlight_file(data_io.read_test_svm())
    features = features.todense()

    print("[INFO] Loading the classifier")
    classifier = data_io.load_model()

    print("[INFO] Making predictions")
    predictions = classifier.predict_proba(features)

    return predictions


def save_to_test(can):
    data = open(data_io.read_test_svm(), "w")
    try:
        for st in can:
            data.write(st + "\n")
        data.close()
    except Exception, e:
        pass

def make_string(label, tmp):
    ret = str(label)
    for key in sorted(tmp.keys()):
        ret += " "
        ret += str(key)
        ret += "|"
        ret += str(tmp[key])

    return ret

def gen_parameters(nodes, conf):
    global prime
    prime = gen_prime(nodes)

    gen_candidate(nodes)
    global candidate
    candidate = sorted(candidate)
    
    can = []
    for i in range(10):
        conf = dict()
        conf["nodes"] = nodes
        k = random.randint(0, len(candidate) - 1)
        conf["range"] = candidate[k]
        conf["gen_tasks"] = nodes / conf["range"]
        k = random.randint(0, len(candidate) - 1)
        conf["drange"] = candidate[k]
        conf["stat_tasks"] = nodes / conf["drange"]
        can.append(conf)
    
    feature_map = dict()

    # Load feature map
    try:
        feature_map_input = open(data_io.feature_map(), "r")
        for line in feature_map_input:
            feature_map[line.split("|")[0]] = int(line.split("|")[1])
        feature_map_input.close()
    except Exception, e:
        pass
    maxn = len(feature_map)
    
    can1 = []

    for i in can:
        x = dict()
        for j in range(maxn):
            x[j] = 0
        for k, v in i.iteritems():
            x[feature_map[k]] = v
        can1.append(x)

    st = []
    for instance in can1:
        st.append(make_string(0.0, instance))
    save_to_test(st)

    prob = estimate()
    minn = prob[0][0]
    j = 0
    for i in range(len(prob)):
        if minn > prob[i][0]:
            minn = prob[i][0]
            j  = i
    return can[j]

def intify(conf):
    for k, v in conf.items():
        conf[k] = int(v)
    return conf

def predict(conf):
    conf = intify(conf)
    return gen_parameters(conf["nodes"], conf)

if __name__=="__main__":
    estimate()
