Examples
========

The following examples illustrate common actions in an autonomous driving application.
They are written in Python, but if you code in JavaScript, you can utilize our helyosjs-sdk package. 
Check the webapp tutorial to learn how to use the helyosjs-sdk.


Get Authorization Token with Login
----------------------------------

In the following snipet, an external application can get the authorization token using GraphiQL. 
Alternatively, the helyos `admin` can create a token using the helyos dashboard.

.. code-block:: python
    :caption:  External applications gets authorization token.

    import requests,  json
    hostname = "https://helyos-server.com"
    username = "myaccount"
    password = "mypassword"
    session = requests.Session()
    session.headers.update({ "Content-Type": "application/json; charset=utf-8"})


    def login(username, password):
        session.headers.pop('Authorization', '')
        graphql_request = {"operationName": "authenticate",
                        "query":""" mutation authenticate($postMessage:  AuthenticateInput!) {
                                        authenticate(input:$postMessage)  {  jwtToken }}
                                """,
                            "variables": {"postMessage": { "username": username, "password":password} }
                            }
        res = session.post(f"{hostname}/graphql", json=graphql_request)
        token = res.json()['data']['authenticate']['jwtToken']
        return token

    auth_token = login(username, password)
    print(f"Authorizaton token: {auth_token}")
    session.headers.update({ "Authorization": f"Bearer {auth_token}"})   



List the Agents in the Yard
----------------------------

.. code-block:: python
    :caption:  Retrieve agents.

    def list_agents(condition={}):
        graphql_request = {"operationName": "allAgents",
                        "query":""" 
                                query allAgents($condition: AgentCondition!) {
                                        allAgents (condition: $condition){
                                        nodes {id,  uuid, geometry}
                                        }
                                    }
                                """,

                                "variables": {"condition": condition }
                            }

        res = session.post(f"{hostname}/graphql", json=graphql_request)
        return res.json()['data']['allAgents']['nodes']

    print(list_agents({"yardId":3}))       


Check also the query `agentById` in the graphiql dashboard: http://localhost:5000/graphiql.


Subscribe to the Position and Sensors Data Stream
-------------------------------------------------

.. code-block:: python
    :caption:  Retrieve agents sensors.

    # !pip install "python-socketio[client]"
    import socketio

    hostname = "https://helyos-server.com" # or wss://helyos-sever.com
    authToken = login(username, password) # see previous example

    headers = {"Content-Type": "application/json; charset=utf-8"}
    auth = {"token": authToken}

    sio = socketio.Client()
    sio.connect(hostname, headers=headers, auth=auth, transports="websocket")

    @sio.event
    def connect():
        print('connection established')

    @sio.on('new_agent_poses')
    def get_agent_data(data):
        """Get all agent sensors. """
        print(data)


    sio.wait() # block thread until disconnection

    #  Message stream:
    # [{'agentId': '1', 'lastMessageTime': '2024-06-04T16:04:22.760Z', 'uuid': 'Bb34069fc5-fdgs-434b-b87e-f19c5435113',
    #   'x': -30000, 'y': 10000, 'z': 0, 'orientation': 0.329, 'orientations': [0.329, 0], 'sensors': {...}]
    # [{'agentId': '1', 'lastMessageTime': '2024-06-04T16:04:22.964Z', 'uuid': 'Bb34069fc5-fdgs-434b-b87e-f19c5435113',
    #   'x': -30000, 'y': 10000, 'z': 0, 'orientation': 0.329, 'orientations': [0.329, 0], 'sensors': {...}] 
    

Subscribe to the agent status update event via WebSocket
--------------------------------------------------------

.. code-block:: python
    :caption:  Retrieve agents status.

    # !pip install "python-socketio[client]"
    import socketio

    hostname = "https://helyos-server.com" # or wss://helyos-sever.com
    authToken = login(username, password) # see previous example

    headers = {"Content-Type": "application/json; charset=utf-8"}
    auth = {"token": authToken}

    sio = socketio.Client()
    sio.connect(hostname, headers=headers, auth=auth, transports="websocket")

    @sio.event
    def connect():
        print('connection established')

    @sio.on('change_agent_status')
    def get_agent_status(data):
        """Get agent status when it changes. """
        print(data)


    sio.wait() # block thread until disconnection

 


Request mission and subscribe to the status updates via WebSocket
--------------------------------------------------------------------------

.. code-block:: python
    :caption:  Mission request.

    import requests, json
    import socketio
    
    # Login: request to the Authorization token should come here
    # 

    auth = {"token": authToken}
    sio = socketio.Client()
    sio.connect(hostname, auth=auth, transports="websocket")

    @sio.on('work_processes_update')
    def get_mission_status(data):
        """Get agent status when it changes. """
        for event in data:
          print(f"mission id #{event['id']} status: {event['status']}")


    def request_mission(mission_type, agents, data={}):     
        graphql_request = { 

        "operationName": "createWorkProcess",
        "query": """mutation createWorkProcess($postMessage: CreateWorkProcessInput!){
                        createWorkProcess(input: $postMessage) {
                            workProcess {id, status }
                        }
                    }
                """,
        "variables": {"postMessage" : {"clientMutationId": "not_used",
                                        "workProcess": {
                                                "status": "dispatched",
                                                "yardUid":"DACHSER_SIM",
                                                "workProcessTypeName": mission_type,
                                                "data": json.dumps(data),
                                                "agentUuids": json.dumps([agents])		
                                          }
                                    }  
                        }
        }
            
        response = session.post(f"{hostname}/graphql", json=graphql_request)
        return response.json()['data']['createWorkProcess']['workProcess']


    mission = request_mission("driving", ["4353452-452355-56346"], {"to": [50.12343, 10.3442]})
    print(mission)

    sio.wait() 

    #  Output
    # {'id': '13', 'status': 'dispatched'}
    # mission id #13 status: preparing resources
    # mission id #13 status: preparing resources
    # mission id #13 status: calculating
    # mission id #13 status: planning_failed
    # mission id #13 status: failed




Request the Canceling of a Mission 
-----------------------------------
To cancel a mission, you need just to change the work process status to "canceling".

.. code-block:: python
    :caption:  Mission request.

    import requests, json
    import socketio

    # Login: request to the Authorization token should come here
    # 

    auth = {"token": authToken}
    sio = socketio.Client()
    sio.connect(hostname, auth=auth, transports="websocket")

    @sio.on('work_processes_update')
    def get_mission_status(data):
        """Get agent status when it changes. """
        for event in data:
        print(f"mission id #{event['id']} status: {event['status']}")



    def cancel_mission(missionId):
        graphql_request = {
                    "operationName": "updateWorkProcessById",
                    "query":""" 
                            mutation updateWorkProcessById($postMessage: UpdateWorkProcessByIdInput!){
                                updateWorkProcessById(input:$postMessage) {
                                        workProcess {id status }
                                }
                            }
                            """,

                        "variables": {"postMessage": {"id":missionId, "workProcessPatch": { "status": "canceling"}} }
                        }

        response = session.post(f"{hostname}/graphql", json=graphql_request)
        return response.json()['data']['updateWorkProcessById']['workProcess']



    mission = cancel_mission(14)
    print(mission)

    sio.wait()

    # Output
    # {'id': '14', 'status': 'canceling'}
    # mission id #14 status: canceling
    # mission id #14 status: canceled



Send instant actions to agents
-------------------------------

Instant actions allow external applications to directly communicate requests to the agent. 
They can be used to change agent settings or to influence or pause running assignments.

.. code-block:: python
    :caption:  Mission request.

    def create_instant_action(instant_action):
            graphql_request = {
            "operationName": "createInstantAction",
            "query": """
                mutation createInstantAction($postMessage: CreateInstantActionInput!) {
                    createInstantAction(input: $postMessage) {
                        instantAction {
                            id,
                            createdAt,
                            agentUuid,
                            error,
                        }
                    }
                }
                """,
            "variables": {
                "postMessage":{"clientMutationId": "not_used", "instantAction": instant_action }
            }
            }

            response = session.post(f"{hostname}/graphql", json=graphql_request)
            result = response.json()

            return result['data']['createInstantAction']['instantAction']


    create_instant_action({"agentUuid":"Ab34069fc5-fdgs-434b-b87e-f19c5435113", "command":"my custom command here..."} )




Advanced Commands
-----------------

All commands issued by the helyOS Dasboard can be performed via GraphQL.
Those are some examples:


Create and update agents programatically
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

There are four classes of agents: 'vehicle', 'assistant', 'tool', 'charge_station'.


.. code-block:: python
    :caption:  Handle agent registration.

    def create_agent(uuid, name, pose, geometry, status, agentClass="vehicle", agentType="truck"):

        agent_data = {'uuid':uuid, 
                    'name': name, 
                    'geometry': json.dumps(geometry),
                    'status': status,
                    'agentClass': agentClass,
                    'agentType': agentType}

        agent_data['x']=pose['x']
        agent_data['y']=pose['y']
        agent_data['orientations']=pose['orientations']
        
        graphql_request = {"operationName": "createAgent",
                            "query":""" 
                                        mutation createAgent($postMessage: CreateAgentInput!){
                                            createAgent(input:$postMessage) { agent{id} }
                                        }""",

                                "variables": {"postMessage": {"agent": agent_data} }
                                }    
        
        response = session.post(f"{hostname}/graphql", json=graphql_request)
        return response.json()


    def update_agent(uuid, name, pose, geometry, status, agentClass="vehicle", agentType="truck"):

        agent_data = {'uuid':uuid, 
                    'name': name, 
                    'geometry': json.dumps(geometry),
                    'status': status,
                    'agentClass': agentClass,
                    'agentType': agentType}

        agent_data['x']=pose['x']
        agent_data['y']=pose['y']
        agent_data['orientations']=pose['orientations']
        
        graphql_request = {"operationName": "updateAgentByUuid",
                            "query":""" 
                                        mutation updateAgentByUuid($postMessage: UpdateAgentByUuidInput!){
                                            updateAgentByUuid(input:$postMessage) { agent{id} }
                                        }""",

                                "variables": {"postMessage": { "uuid": uuid, "agentPatch": agent_data} }
                                }    
        
        response = session.post(f"{hostname}/graphql", json=graphql_request)
        return response.json()



Updating multiple map objects
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This example demonstrates how to insert multiple mutations into a single GraphQL query. 
This approach should be used to minimize latency when updating many instances. 
For applications where updates to map objects are very frequent,
such as dynamic objects (over 1 Hz), consider performing the updates via RabbitMQ using an agent assistant.

.. code-block:: python
    :caption:  Update map objects.

    def update_map_objects(map_objects):
    # Start building the query and variables
        query_parts = []
        variable_definitions = []
        variables = {}

        for i, map_object in enumerate(map_objects):
            mobj_id = map_object['id']
            mobj_patch = map_object

            # Create a unique alias and variable name for each mutation
            alias = f"mutation{i}"
            variable_name = f"postMessage{i}"
            
            # Append the mutation part for this object
            query_parts.append(f"""
                {alias}: updateMapObjectById(input: ${variable_name}) {{
                    mapObject {{ id }}
                }}
            """)
            
            # Add the variable definition for this object
            variable_definitions.append(f"${variable_name}: UpdateMapObjectByIdInput!")
            
            # Add the variables for this object
            variables[variable_name] = {"mapObjectPatch": mobj_patch, "id": mobj_id}

        # Combine the query parts into a single query string
        query = "mutation updateMapObjects(" + ", ".join(variable_definitions) + ") {" + "\n".join(query_parts) + "\n}"

        graphql_request = {
            "operationName": "updateMapObjects",
            "query": query,
            "variables": variables
        }
        print(query)
        response = session.post(f"{hostname}/graphql", json=graphql_request)
        return response.json()

        res = update_map_objects([
                        {"data": json.dumps({
                                        "top":9999,
                                        "bottom":0,
                                        "points":[[21145.495567237958,-25642.97220017761]]
                                }),
                        "type": "obstacle",
                        "dataFormat": "trucktrix",
                        "yardId": 3,
                        "id":5,
                        },
                          
                        {"data": json.dumps({
                                        "top":9999,
                                        "bottom":0,
                                        "points":[[11145.495567237958,-25642.97220017761]]
                                      }),
                        "type": "obstacle",
                        "dataFormat": "trucktrix",
                        "yardId": 3,
                        "id":6,
                        }                     
                    ])
        print(res)
        # Output:
        # mutation updateMapObjects($postMessage0: UpdateMapObjectByIdInput!, $postMessage1: UpdateMapObjectByIdInput!) {
        #     mutation0: updateMapObjectById(input: $postMessage0) {
        #         mapObject { id }
        #     }
        #     mutation1: updateMapObjectById(input: $postMessage1) {
        #         mapObject { id }
        #     }
        #}
        #{'data': {'mutation0': {'mapObject': {'id': '5'}}, 'mutation1': {'mapObject': {'id': '6'}}}}

    

Updating a microservice registration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In very special cases, the external application can change a microservice parameter or even rewrite a mission recipe.
The application must have admin permissions.






