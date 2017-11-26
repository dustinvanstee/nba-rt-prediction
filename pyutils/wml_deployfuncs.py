# %load deployfuncs.py
import urllib3, requests
import json


def get_token(creds):
    # This block gets your authorization token
    mltoken = 0
    headers = urllib3.util.make_headers(basic_auth='{}:{}'.format(creds["username"], creds["password"]))
    #url = '{}/v2/identity/token'.format(creds["url"])
    url = '{}/v3/identity/token'.format(creds["url"])
    response = requests.get(url, headers=headers)
    mltoken = json.loads(response.text).get('token')
    return mltoken

def get_published_models(creds) :
    # This block gets your authorization token
    mltoken = get_token(creds)

    #v2
    #header_online = {'Content-Type': 'application/json', 'Authorization': mltoken}
    #published_models = '{}/v2/published_models'.format(creds["url"])
    #response = requests.get(published_models, headers=header_online)
    
    #return json.loads(response.text)

    #V3
    # Use this to get published model url
    endpoint_instance = creds["url"] + "/v3/wml_instances/" + creds["instance_id"]
    #header = {'Content-Type': 'application/json', 'Authorization': mltoken}
    header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}

    response_get_instance = requests.get(endpoint_instance, headers=header)
    # print response_get_instance
    # print response_get_instance.text
    
    published_model_url = json.loads(response_get_instance.text)["entity"]["published_models"]["url"]
    #print published_model_url

    # now get published models
    response_get = requests.get(published_model_url, headers=header)
    #print response_get
    #print response_get.text
    
    published_models = {}
    #for i in range(0,len(json.loads(response.text)["resources"])) :
    print "## Published Model Summary ##"
    for i in range(0,len(json.loads(response_get.text)["resources"])) :
        print "# Published Model " + str(i) + " " + json.loads(response_get.text)["resources"][i]["metadata"]["guid"] + " " + json.loads(response_get.text)["resources"][i]["entity"]["name"]
        #print json.loads(response.text)["resources"][i]["metadata"]["guid"]
        #print json.loads(response.text)["resources"][i]["entity"]["name"]

     #return json.loads(response.text)
    return json.loads(response_get.text)


#print get_published_models(creds)["resources"][0]["metadata"]["guid"]
#print get_published_models(creds)["resources"][0]["entity"]["name"]

def delete_model_by_id(creds, published_model_id) :
    #9578a55a-5129-4498-9793-efb95c3fc280
    # This block gets your authorization token
    mltoken = get_token(creds)

    #header_online = {'Content-Type': 'application/json', 'Authorization': mltoken}
    header_online = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}
    published_models = '{}/v2/published_models/{}'.format(creds["url"],published_model_id)
    response = requests.delete(published_models, headers=header_online)
    #mltoken = json.loads(response.text).get('token')
    if( response.status_code == 204) :
        print "Successfully deleted model"
    else :
        print "Unsuccessful deletion"
        print response.text
        
    print "status = " + str(response.status_code)
    return response

def delete_model_by_name(creds, model_name) :
    published_models_json = get_published_models(creds)
    published_model_id_list = []
    for x in published_models_json['resources'] :
        if(x['entity']['name'] == model_name) :
            published_model_id_list.append(x['metadata']['guid'])
    for published_model_id in published_model_id_list :                                
        if(published_model_id == "") :
            print "No Model Found .. skipping delete ..."
        else :
            print "Deleting Model {0} {1}".format(model_name, published_model_id)
            delete_model_by_id(creds, published_model_id)

def deploy_model(creds, published_models_json, published_model_name_or_id) :
    mltoken = get_token(creds)
    
     
    #header_online = {'Content-Type': 'application/json', 'Authorization': mltoken}
    header_online = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}

    # get deployment endpoint
    # can pass either model name or model id .. just to make it a little easier
    [endpoint_deployments] = [x['entity']['deployments']['url'] for x in published_models_json['resources'] 
                              if ((x['entity']['name'] == published_model_name_or_id) or (x['metadata']['guid'] == published_model_name_or_id))]

    payload_online = {"name": "Auto Deployment ", "description": "My Cool Deployment", "type": "online"}
    response_online = requests.post(endpoint_deployments, json=payload_online, headers=header_online)
    # print json.loads(response_online.text).get('entity')
    
    scoring_url = json.loads(response_online.text).get('entity').get('scoring_url')
    print scoring_url
    return scoring_url

# Returns the URL and name of the deployments
def get_deployed_models(creds) :
    pm_json = get_published_models(creds)
    # This block gets your authorization token
    # This is a stub to implement this when you get some time

def save_model_by_name(creds, model_name, model_in, training_data) : 
    from repository.mlrepositoryclient import MLRepositoryClient
    from repository.mlrepositoryartifact import MLRepositoryArtifact
    ml_repository_client = MLRepositoryClient(creds["url"])
    ml_repository_client.authorize(creds["username"], creds["password"])
    model_artifact = MLRepositoryArtifact(model_in, training_data=training_data, name=model_name)
    
    #Add a check to remove models with the same name.  WML allows this,but its bad practice IMO
    delete_model_by_name(creds, model_name)
    
    saved_model = ml_repository_client.models.save(model_artifact)
    
    return saved_model.uid

def score_example(creds, scoring_url, test_example_json) :

    # Get the scoring endpoint from the WML service
    mltoken = get_token(creds)
    header_online = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}

    # API call here
    response_scoring = requests.post(scoring_url, data=test_example_json, headers=header_online)
    print response_scoring.text
    return response_scoring.text

# This only works in the notebook!
def retrain_and_deploy(creds,newdf, model_name) :
    
    # Retrain model with new data
    pipline_new, retrained_model = build_model(newdf)
    
    # Delete Old Model if exists
    delete_model_by_name(creds, model_name)
    
    # add evaluation criteria ?? assume, you are redeploying for now
    published_model_id = save_model_by_name(creds, model_name, retrained_model, newdf) 
    
    # get all the published models metadata
    published_models_json = get_published_models(creds)
    
    # now deploy this new model you pushed
    scoring_url = deploy_model(creds, published_models_json, published_model_id)
    
    print "Here is the new scoring URL "
    #5. def test_model(url)
    return scoring_url
