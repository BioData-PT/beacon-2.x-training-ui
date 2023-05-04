from pymongo import MongoClient
from app.schemas import INDIVIDUALS_DICT, BIOSAMPLES_DICT, FILTERING_TERMS_DICT
import json, re, logging

def get_db_handle(db_name, host, port, username, password):
    client = MongoClient(host=host,
                         port=int(port),
                         username=username,
                         password=password
                        )
    db_handle = client[db_name]
    return db_handle, client

def get_collection_handle(db_handle,collection_name):
    return db_handle[collection_name]



def parse_query(request, schema):
    error = ""
    # separate key-value pairs
    request_list = request.split(",")
    # info to identidy each key, operator and value
    pattern = '(.+)([=|<|>])(.+)'
    operator_dict = {
        "=": "$eq",
        ">": "$gt",
        "<": "$lt"
    }
    # loop through every key-value pair and parse it
    query_list_normal_obj = [] 
    query_list_array_obj = []
    for element in request_list:
        element = element.strip()
        try:
            m = re.match(pattern, element, re.IGNORECASE)
            key_full = m.group(1)
            key_list = key_full.split(".")
            key = key_list[0]
            value = m.group(3)
            operator = m.group(2)
        except:
            if element in FILTERING_TERMS_DICT.keys():
                key_full = FILTERING_TERMS_DICT[element][1]
                key_list = key_full.split(".")
                key = key_list[0]
                value = element
                operator = "="
            else:
                # this filtering term is not registered
                error = "Some of the query terms are incorrect/not available. Please, check the schema, the filtering terms and the query syntax and try again."
                continue
        
        # detect if value if string or ontology
        key_type = ".id" if ":" in value else ".label"  # useful if object_id_label
        
        # for this UI we assume if the value is float, the key is measurements ('array_object_measures')
        try:
            value= float(value)
            str_operator = operator_dict[operator]
            # control cases where the user didn't put commas in the query
            if not key.startswith(tuple(schema.keys())):
                query_measure = f"{{'measures': {{'$elemMatch': {{'assayCode{key_type}': '{key}',  'measurementValue.value': {{'{str_operator}': {value}}}}}}} }}"
                query_list_array_obj.append(query_measure)
            else:
                error = "Some of the query terms are incorrect/not available. Please, check the schema, the filtering terms and the query syntax and try again."
        # if not, we can have 'object_id_label', 'simple', 'array_object_id_label' or 'array_object_complex'
        except ValueError:
            if key in schema and schema[key] == "object_id_label":
                query_normal = f"'{key}{key_type}': '{value}'"   
                query_list_normal_obj.append(query_normal)
            elif key in schema and schema[key] == "simple":
                query_normal = f"'{key}': '{value}'"   
                query_list_normal_obj.append(query_normal)
            elif key in schema and schema[key] == "array_object_id_label":
                key_sub = ".".join(key_list[1:])
                query_array = f"{{'{key}': {{'$elemMatch': {{'{key_sub}{key_type}': '{value}'}}}}}}"
                query_list_array_obj.append(query_array)
            elif key in schema and schema[key] == "array_object_complex":
                key_sub = ".".join(key_list[1:])
                query_array = f"{{'{key}': {{'$elemMatch': {{'{key_sub}': '{value}'}}}}}}"
                query_list_array_obj.append(query_array)
            else:
                error = "Some of the query terms are incorrect/not available. Please, check the schema, the filtering terms and the query syntax and try again."
                
    # prepare query string            
    query_string_array_obj = ""
    query_string_normal_obj = ""
    if query_list_array_obj:
        query_string_array_obj = "'$and':[" +  ",".join(query_list_array_obj) + "]"
    if query_list_normal_obj: 
        query_string_normal_obj = ",".join(query_list_normal_obj)

    comma = "," if query_string_array_obj and query_string_normal_obj else ""
    query_string = ""
    query_string = "{" + query_string_array_obj + comma + query_string_normal_obj + "}"

    query_string = query_string.replace("'", '"')
    query_json = json.loads(query_string)

    return query_json, error

# like parse_query but requests API instead of DB
def parse_query_api(request, schema):
    error = ""
    # separate key-value pairs
    request_list = request.split(",")
    # info to identidy each key, operator and value
    pattern = '(.+)([=|<|>])(.+)'
    operator_list = ["=","<",">","!","<=",">="]

    # loop through every key-value pair and parse it
    query_list_normal_obj = [] 
    query_list_array_obj = []
    for element in request_list:
        element = element.strip()
        try:
            m = re.match(pattern, element, re.IGNORECASE)
            key_full = m.group(1).strip()
            key_list = key_full.split(".")
            key = key_list[0]
            value = m.group(3).strip()
            operator = m.group(2).strip()
        except: # no operator
            if element in FILTERING_TERMS_DICT.keys():
                key_full = FILTERING_TERMS_DICT[element][1]
                key_list = key_full.split(".")
                key = key_list[0]
                value = element
                operator = "="
            else:
                # this filtering term is not registered
                error = "Some of the query terms are incorrect/not available. Please, check the schema, the filtering terms and the query syntax and try again."
                continue
        
        # detect if value is a string or ontology code
        key_type = ".id" if ":" in value else ".label"  # useful if object_id_label
        
        # for this UI we assume if the value is float, the key is measurements ('array_object_measures')
        try:
            value= float(value)
            
            if operator not in operator_list:
                raise ValueError(f"Operator not accepted: {operator}")
            
            # control cases where the user didn't put commas in the query
            if not key.startswith(tuple(schema.keys())):
                query_measure = f"{{'measures': {{'$elemMatch': {{'assayCode{key_type}': '{key}',  'measurementValue.value': {{'{operator}': {value}}}}}}} }}"
                query_list_array_obj.append(query_measure)
            else:
                error = "Some of the query terms are incorrect/not available. Please, check the schema, the filtering terms and the query syntax and try again."
        # if not, we can have 'object_id_label', 'simple', 'array_object_id_label' or 'array_object_complex'
        except ValueError as ex:
            if key in schema and schema[key] == "object_id_label":
                query_normal = f"'{key}{key_type}': '{value}'"   
                query_list_normal_obj.append(query_normal)
            elif key in schema and schema[key] == "simple":
                query_normal = f"'{key}': '{value}'"   
                query_list_normal_obj.append(query_normal)
            elif key in schema and schema[key] == "array_object_id_label":
                key_sub = ".".join(key_list[1:])
                query_array = f"{{'{key}': {{'$elemMatch': {{'{key_sub}{key_type}': '{value}'}}}}}}"
                query_list_array_obj.append(query_array)
            elif key in schema and schema[key] == "array_object_complex":
                key_sub = ".".join(key_list[1:])
                query_array = f"{{'{key}': {{'$elemMatch': {{'{key_sub}': '{value}'}}}}}}"
                query_list_array_obj.append(query_array)
            else:
                error = f"Some of the query terms are incorrect/not available. Please, check the schema, the filtering terms and the query syntax and try again."
                logging.error(f"{error}.\nException msg: {ex.message}")
                
    # prepare query string            
    query_string_array_obj = ""
    query_string_normal_obj = ""
    if query_list_array_obj:
        query_string_array_obj = "'$and':[" +  ",".join(query_list_array_obj) + "]"
    if query_list_normal_obj: 
        query_string_normal_obj = ",".join(query_list_normal_obj)

    comma = "," if query_string_array_obj and query_string_normal_obj else ""
    query_string = ""
    query_string = "{" + query_string_array_obj + comma + query_string_normal_obj + "}"

    query_string = query_string.replace("'", '"')
    query_json = json.loads(query_string)
    
    logging.debug(f"query_json: {json.dumps(query_json, indent=2, sort_keys=True)}")

    return query_json, error 