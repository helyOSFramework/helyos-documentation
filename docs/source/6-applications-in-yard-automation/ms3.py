from flask import Flask, jsonify, request
from my_calculations import calculate_analytics, save_database
app = Flask(__name__)

@app.post("/storage/")
def getPath():
    request_body = request.get_json() 
    request_data = request_body['request']
    context = request_body['context']

    analytics = calculate_analytics(request_data, context)
    save_database(analytics)
    
    response =  {
                "status" : "ready"
                }
    
    return jsonify(response)
