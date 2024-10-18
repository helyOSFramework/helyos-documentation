from flask import Flask, jsonify, request
from calculations_1 import calculateA, calculateB
app = Flask(__name__)

@app.post("/plan_job/")
def getPath():
    request_body = request.get_json() 
    request_data = request_body['request']
    context = request_body['context']

    assignment1A = calculateA(request_data, context)
    assignment1B = calculateB(request_data, context)
    
    response =  {
                "status" : "ready",
                "results":[{
                            "agent_uuid": 'AGENT-A',
                            "assignment": assignment1A
                            },
                            {
                            "agent_uuid": 'AGENT-B',
                            "assignment": assignment1B
                            }],
                "dispatch_order" : [ [0] , [1] ]
                }
    
    return jsonify(response)