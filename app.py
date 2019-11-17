from flask import Flask, render_template

import requests
import json

app = Flask(__name__)

MOLOCH_SUBGRAPH_URL="https://api.thegraph.com/subgraphs/name/molochventures/moloch"
QUERY={'query':"""{members{id,shares}}"""}

def moloch():
    request=requests.post(MOLOCH_SUBGRAPH_URL, json=QUERY)
    if request.status_code == 200:
        data = request.json()
        data = data['data']['members']
        data = [(item['id'], int(item['shares'])) for item in data]
        return sorted(filter(lambda item: item[1]!=0, data), reverse=True, key=lambda item: item[1])
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))

def banzhaf(weights, quota=None):
    """Quick and dirty implementation of an absolute Banzhaf power index
       using the generator function approach to calculation. --jbrukh"""
    total = sum(weights)                      
    if not quota:
        quota = int(total/2 + 1)
    n = len(weights)                              
    polynomial = [1] + total*[0]
    order = 0
    p = polynomial[:]
    for weight in weights:
        order = order + weight
        offset = weight*[0] + polynomial
        for j in range(order + 1):
            p[j] = polynomial[j] + offset[j]
        polynomial = p[:]
    power = (n * [0])                      
    swings = (quota * [0])                         
    for i in range(n):                             
        for j in range(quota):                   
            if (j<weights[i]):
                swings[j] = polynomial[j]
            else:
                swings[j] = polynomial[j] - swings[j - weights[i]]
        for k in range(weights[i]):                             
            power[i] += swings[quota-1-k]
    denominator = float(sum(polynomial)/2)
    index = map(lambda x: x / denominator, power)
    return (index, total, quota)

@app.template_filter()
def pct(s):
    return '%.3f' % (100 * s)   

@app.route('/')
def hello_world():
    l = moloch()
    weights = [item[1] for item in l]
    banzhaf_index, total, quota = banzhaf(weights)
    result = zip(l, banzhaf_index)
    return render_template('index.html', total=total, quota=quota, result=result)        

if __name__ == '__main__':
    app.run()
