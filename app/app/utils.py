from pymongo import MongoClient
from app.schemas import INDIVIDUALS_DICT, BIOSAMPLES_DICT, FILTERING_TERMS_DICT
import json, re, logging
from app.settings import SKIP_DEFAULT, LIMIT_DEFAULT

LOG:logging.Logger = logging.getLogger(__name__)

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


# returns empty POST payload
def get_payload_default():
    payload = {}
    payload["meta"] = {"apiVersion": "2.0"}
    payload["query"] = {
        "filters": [], 
        "includeResultsetResponses":"HIT", 
        "pagination": {
            "skip": SKIP_DEFAULT, 
            "limit": LIMIT_DEFAULT
        },
        "testMode": False,
        "requestedGranularity": "record"
    }
    
    return payload

##################################################
### VARIANT
##################################################

def get_variant_query(input_query):
    error_message = ""
    
    #pattern = f'({ALLOWED_CHARS_NAME}+)(<=|>=|=|<|>|!)({ALLOWED_CHARS_VALUE}+)$'
    pattern = '^(X|Y|MT|[1-9]|1[0-9]|2[0-2])\s*\:\s*(\d+)\s+([ATCGN]+)\s*\>\s*([ATCGN]+)\s*$'
    
    m = re.match(pattern, input_query, re.IGNORECASE)
    
    if not m:
        error_message = "The query pattern is wrong. Please, use 'chr : position reference > alternate' and try again."
        return None, error_message
    
    chromosome = m.group(1)
    start = m.group(2)
    reference = m.group(3).upper()
    alternate = m.group(4).upper()
    
    LOG.info(f"Query: {chromosome} : {start} {reference} > {alternate}")
    
    query_json = get_payload_default()
    query_json["query"]["requestParameters"] = {
        "Chromosome": chromosome,
        "start": start,
        # get this precise position 
        # instead of all that start on there
        "end": str(int(start)+1),
        "referenceBases": reference,
        "alternateBases": alternate
    }
    
    return query_json, error_message

##################################################
### REGION
##################################################

def get_region_query(input_query):
    error_message = ""
    
    pattern = '^(X|Y|MT|[1-9]|1[0-9]|2[0-2])\s*\:\s*(\d+)\s*-\s*(\d+)\s*$'
    
    m = re.match(pattern, input_query, re.IGNORECASE)
    
    if not m:
        error_message = "The query pattern is wrong. Please, use 'chr : <start_position> <end_position>' and try again."
        return None, error_message
    
    chromosome = m.group(1)
    start = m.group(2)
    end = m.group(3)
    
    LOG.info(f"Query: {chromosome} : {start} - {end}")
    
    query_json = get_payload_default()
    query_json["query"]["requestParameters"] = {
        "Chromosome": chromosome,
        "start": start,
        "end": end,
    }
    
    return query_json, error_message

##################################################
### PHENOCLINIC
##################################################

# NOT USED ANYMORE
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

    
# Receives message query (like "name = John")
# Returns json to query the API using filters
# like parse_query but requests API instead of DB
def parse_query_api(request):
    error_message = ""
    # separate key-value pairs
    request_list = request.split(",")
    # info to identidy each key, operator and value
    ALLOWED_CHARS_NAME = r"[a-z|A-Z|0-9|\.|\-|_| ]"
    ALLOWED_CHARS_VALUE = r"[a-z|A-Z|0-9|\.|\-|_| |:]"
    pattern = f'({ALLOWED_CHARS_NAME}+)(<=|>=|=|<|>|!)({ALLOWED_CHARS_VALUE}+)$'
    # operator_list = ["=","<",">","!","<=",">="]

    # loop through every key-value pair and parse it
    filter_list = []
    for element in request_list:
        element = element.strip()
        logging.debug(f"debug parse_query - element: {element}")
        try: # <id> <operator> <value>
            m = re.match(pattern, element, re.IGNORECASE)
            key_full = m.group(1).strip()
            key_list = key_full.split(".")
            key = key_list[0]
            value = m.group(3).strip()
            operator = m.group(2).strip()
        except: # just value
            if element in FILTERING_TERMS_DICT.keys():
                key_full = FILTERING_TERMS_DICT[element][1]
                key_list = key_full.split(".")
                key = key_list[0]
                value = element
                operator = "="
            else:
                # this filtering term is not registered
                error_message = f"Some of the query terms are incorrect/not available ({element}). Please, check the schema, the filtering terms and the query syntax and try again."
                continue
        
        filter = { 
                  "id": key_full,
                  "operator": operator,
                  "value": value
                  }
        
        logging.debug(f"parse_query: filter before conversion: {filter}")
        
        # detect if value is a string or ontology code
        key_type = "id" if ":" in value else "label"  # useful if object_id_label
        
        # check if need to add key_type
        if key_list[-1] not in ("id","label"):
            filter["id"] = f"{key_full}.{key_type}"
            LOG.debug(f"parse_query: filter id changed to {filter['id']}")
        
        filter_list.append(filter)
    
    #query_json = json.loads(query_string)
    query_json = get_payload_default()
    query_json["query"]["filters"] = filter_list
    
    logging.debug(f"parsed query_json: {json.dumps(query_json, indent=2)}")

    return query_json, error_message


##################################################
### COHORTS
##################################################

def get_cohort_query(input_query):
    error_message = ""
    
    LOG.info(f"Query: (All Cohorts)")
    
    query_json = get_payload_default()
    
    return query_json, error_message