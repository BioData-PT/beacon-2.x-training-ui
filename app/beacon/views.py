from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.http import Http404
from django.shortcuts import render
import re
import json
import os
import requests
import logging

from app.utils import get_db_handle, get_collection_handle


##################################################
### DATABASE CONFIG
##################################################

# Get environment variables or use default
DATABASE_NAME = os.getenv('DATABASE_NAME', 'beacon')
DATABASE_HOST = os.getenv('DATABASE_HOST', 'mongo')
DATABASE_PORT = os.getenv('DATABASE_PORT', '27017')
BEACON_PROT = os.getenv('BEACON_PROT', 'http') # could be https
BEACON_HOST = os.getenv('BEACON_HOST', 'beacon')
BEACON_PORT = os.getenv('BEACON_PORT', '9050')
BEACON_LOCATION = os.getenv('BEACON_LOCATION', '/api/')
USERNAME = os.getenv('USERNAME', 'root')
PASSWORD = os.getenv('PASSWORD', 'example')

db_handle, mongo_client = get_db_handle(DATABASE_NAME, DATABASE_HOST, DATABASE_PORT, USERNAME, PASSWORD)

print(f"\nConnecting to {DATABASE_HOST}:{DATABASE_PORT} {DATABASE_NAME} as {USERNAME}")

# Test connection
try:
    server_info = mongo_client.server_info()
except:
    print("\nThe connection to the DB could not be made. Please, check the DB and try to initiate the Beacon app again.")
    exit(0)

# Test data in DB
try:
    individuals_handle = get_collection_handle(db_handle, "individuals")
    individuals_test = len(list(individuals_handle.find_one()))
    assert individuals_test > 0
except:
    print("\nThe DB does not contain the Beacon test data. Please, check the DB and the loading step and try to initiate the Beacon app again.")
    exit(0)


##################################################
### COHORTS
##################################################

def cohorts(request):
    collection_handle = get_collection_handle(db_handle, "cohorts")

    try:
        results = list(collection_handle.find({}))
        count = len(results)
        keys = set([k for result in results for k in result.keys()])

    except:
        error_message = "Something went wrong, please try again."
        context = {
            'error_message': error_message,
            'count': 0,
            'results': [],
            'cookies': request.COOKIES
        }
        return render(request, 'beacon/cohorts_results.html', context)

    context = {
        'error_message': None,
        'count': count,
        'results': results,
        'keys': keys,
        'cookies': request.COOKIES
    }

    return render(request, 'beacon/cohorts_results.html', context)


##################################################
### VARIANT
##################################################

def variant(request):
    context = {
        'error_message': None,
        'cookies': request.COOKIES,
    }
    return render(request, 'beacon/variant.html', context)

def variant_response(request):
    try:
        query = request.POST['query']
    except KeyError:
        error_message = "Something went wrong with the request, please try again."
        return render(request, 'beacon/variant.html', {
            'error_message': error_message,
            'cookies': request.COOKIES,
            'query': query
        })

    pattern = '^(X|Y|MT|[1-9]|1[0-9]|2[0-2])\s*\:\s*(\d+)\s+([ATCGN]+)\s*\>\s*([ATCGN]+)$'
    m = re.match(pattern, query, re.IGNORECASE)
    if not m:
        error_message = "The query pattern is wrong. Please, use 'chr : position reference > alternate' and try again."
        return render(request, 'beacon/variant_results.html', {
            'error_message': error_message,
            'cookies': request.COOKIES,
            'count': 0,
            'results': [],
            'query': query
        })
    chromosome = m.group(1)
    start = int(m.group(2))
    reference = m.group(3).upper()
    alternate = m.group(4).upper()

    print(f"Query: {chromosome} : {start} {reference} > {alternate}")

    # our test DB only contains one chromosome (22)
    # raise error if another chr is used
    #if chromosome != "22":
    #    error_message = "This Beacon only contains chromosome 22 data. Please, use this chromosome in the query."
    #    return render(request, 'beacon/variant_results.html', {
    #        'error_message': error_message,
    #        'cookies': request.COOKIES,
    #        'count': 0,
    #        'results': [],
    #        'query': query
    #    })

    collection_handle = get_collection_handle(db_handle, "genomicVariations")
    results = list(collection_handle.find({"_position.refseqId": chromosome, "_position.start": start, "variation.referenceBases": reference, "variation.alternateBases": alternate}))
    count = len(results)
    keys = set([k for result in results for k in result.keys()])

    context = {
        'error_message': None,
        'cookies': request.COOKIES,
        'count': count,
        'results': results,
        'query': query,
        'keys': keys
    }

    return render(request, 'beacon/variant_results.html', context)

##################################################
### REGION
##################################################

def region(request):
    context = {
        'cookies': request.COOKIES,
        'error_message': None,
    }
    return render(request, 'beacon/region.html', context)

def region_response(request):
    try:
        query = request.POST['query']
    except KeyError:
        error_message = "Something went wrong with the request, please try again."
        return render(request, 'beacon/region.html', {
            'cookies': request.COOKIES,
            'error_message': error_message,
            'query': query
        })

    pattern = '^(X|Y|MT|[1-9]|1[0-9]|2[0-2])\s*\:\s*(\d+)\s*-\s*(\d+)$'
    m = re.match(pattern, query, re.IGNORECASE)
    if not m:
        error_message = "The query pattern is wrong. Please, use 'chr : start - end' and try again."
        return render(request, 'beacon/region_results.html', {
            'cookies': request.COOKIES,
            'error_message': error_message,
            'query': query
        })
    chr = m.group(1)
    start = int(m.group(2))
    end = int(m.group(3))

    print(f"Query: {chr} : {start} - {end} ")

    # our test DB only contains one chromosome (22)
    # raise error if another chr is used
    #if chr != "22":
    #    error_message = "This Beacon only contains chromosome 22 data. Please, use this chromosome in the query."
    #    return render(request, 'beacon/region_results.html', {
    #        'cookies': request.COOKIES,
    #        'error_message': error_message,
    #        'query': query
    #    })

    # notice chr is not used in the query
    collection_handle = get_collection_handle(db_handle, "genomicVariations")
    results = list(collection_handle.find({"_position.start": {"$gte": start}, "_position.end": {"$lte":end }}))
    count = len(results)
    keys = set([k for result in results for k in result.keys()])

    context = {
        'cookies': request.COOKIES,
        'error_message': None,
        'count': count,
        'results': results,
        'query': query,
        'keys': keys
    }

    return render(request, 'beacon/region_results.html', context)

##################################################
### PHENOCLINIC
##################################################

# Custom dicts to define the 'type' of object
INDIVIDUALS_DICT = {
    "diseases": "array_object_complex",
    "ethnicity": "object_id_label",
    "exposures": "array_object_complex",
    "geographicOrigin": "object_id_label",
    "id": "simple",
    "interventionsOrProcedures": "array_object_complex",
    "measures": "array_object_measures",
    "pedigrees": "array_object_complex",
    "phenotypicFeatures": "array_object_complex",
    "sex": "object_id_label",
    "treatments": "array_object_complex"
}

BIOSAMPLES_DICT = {
    "biosampleStatus": "object_id_label",
    "collectionDate": "simple",
    "collectionMoment": "simple",
    "diagnosticMarkers": "array_object_id_label",
    "histologicalDiagnosis": "object_id_label",
    "id": "simple",
    "individualId": "simple",
    "measurements": "array_object_measures",
    "obtentionProcedure": "object_complex",
    "pathologicalStage": "array_object_id_label",
    "pathologicalTnmFinding": "array_object_id_label",
    "phenotypicFeatures": "array_object_complex",
    "sampleOriginDetail": "object_id_label",
    "sampleOriginType": "object_id_label",
    "sampleProcessing": "object_id_label",
    "sampleStorage": "object_id_label",
    "tumorGrade": "object_id_label",
    "tumorProgression": "object_id_label",
}

# Filtering terms dict as 'filtering term: (target entity, target schema term, label)'
FILTERING_TERMS_DICT = {
    "female": ("individuals", "sex.label", None),
    "NCIT:C16576": ("individuals", "sex.id", "female"),
    "male": ("individuals", "sex.label", None),
    "NCIT:C20197": ("individuals", "sex.id", "male"),
    "England": ("individuals", "geographicOrigin.label", None),
    "GAZ:00002641": ("individuals", "geographicOrigin.id", "England"),
    "Northern Ireland": ("individuals", "geographicOrigin.label", None),
    "GAZ:00002638": ("individuals", "geographicOrigin.id", "Northern Ireland"),
    "Chinese": ("individuals", "ethnicity.label", None),
    "NCIT:C41260": ("individuals", "ethnicity.id", "Chinese"),
    "Black or Black British": ("individuals", "ethnicity.label", None),
    "NCIT:C16352": ("individuals", "ethnicity.id", "Black or Black British"),
    "blood": ("biosamples", "sampleOriginType.label", None),
    "UBERON:0000178": ("biosamples", "sampleOriginType.id", "blood"),
    "reference sample": ("biosamples", "biosampleStatus.label", None),
    "EFO:0009654": ("biosamples", "biosampleStatus.id", "reference sample"),
    "asthma": ("individuals", "diseases.diseaseCode.label", None),
    "ICD10:J45": ("individuals", "diseases.diseaseCode.id", "asthma"),
    "obesity": ("individuals", "diseases.diseaseCode.label", None),
    "ICD10:E66": ("individuals", "diseases.diseaseCode.id", "obesity"),
}

def phenoclinic(request):
    context = {
        'cookies': request.COOKIES,
        'error_message': None,
    }
    return render(request, 'beacon/phenoclinic.html', context)

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

"""
def phenoclinic_response(request):
    try:
        target_collection = request.POST['target']
        query_request = request.POST['query']
    except KeyError:
        error_message = "Something went wrong with the request, please try again."
        return render(request, 'beacon/phenoclinic_results.html', {
            'cookies': request.COOKIES,
            'error_message': error_message,
            'target_collection': target_collection,
            'query': query_request
        })

    collection_handle = get_collection_handle(db_handle, target_collection)

    schema = INDIVIDUALS_DICT if target_collection == "individuals" else BIOSAMPLES_DICT
    query_json, error_message = parse_query(query_request, schema)
    if not query_json:
        error_message = "The query string could not be prepared, please check the schema and try again. Remember to separate the key-value pairs with comma."
        return render(request, 'beacon/phenoclinic_results.html', {
            'cookies': request.COOKIES,
            'error_message': error_message,
            'target_collection': target_collection,
            'query': query_request
        })
    print(f"Query: {target_collection} {query_json} ")
    results = list(collection_handle.find(query_json))
    count = len(results)
    keys = set([k for result in results for k in result.keys()])
    context = {
        'cookies': request.COOKIES,
        'error_message': error_message,
        'count': count,
        'results': results,
        'target_collection': target_collection,
        'query': query_request,
        'keys': keys
    }
    return render(request, 'beacon/phenoclinic_results.html', context)
"""

# USING API
def phenoclinic_response(request: HttpRequest):
    
    try:
        # debug prints
        logging.info(f"Request: {request.POST}")
        # =================
        
        target_collection = request.POST['target']
        query_request = request.POST['query']
    except KeyError:
        error_message = "Something went wrong with the request, please try again."
        return render(request, 'beacon/phenoclinic_results.html', {
            'cookies': request.COOKIES,
            'error_message': error_message,
            'target_collection': target_collection,
            'query': query_request
        })

    collection_handle = get_collection_handle(db_handle, target_collection)

    schema = INDIVIDUALS_DICT if target_collection == "individuals" else BIOSAMPLES_DICT
    query_json, error_message = parse_query(query_request, schema)
    if not query_json:
        error_message = "The query string could not be prepared, please check the schema and try again. Remember to separate the key-value pairs with comma."
        return render(request, 'beacon/phenoclinic_results.html', {
            'cookies': request.COOKIES,
            'error_message': error_message,
            'target_collection': target_collection,
            'query': query_request
        })
    print(f"Query: {target_collection} {query_json} ")
    
    
    #results = list(collection_handle.find(query_json))
    
    payload = {"meta":{"apiVersion": "2.0"}, "query": {"filters": [], "includeResultsetResponses": "HIT", "pagination":{"skip":0, "limit":10}, "testMode": False, "requestedGranularity": "record"} }
    url = f"{BEACON_PROT}://{BEACON_HOST}:{BEACON_PORT}{BEACON_LOCATION}individuals/"
    
    logging.info(f"Debug: payload: {payload}")
    logging.info(f"Debug: URL = {url}")
    
    try:
        results = requests.post(url=url, json=payload)
    except KeyError:
        error_message = "Something went wrong while trying to access the API, please try again."
        return render(request, 'beacon/phenoclinic_results.html', {
        'cookies': request.COOKIES,
        'error_message': error_message,
        'target_collection': target_collection,
        'query': query_request
    })
    
    
    logging.info(f"Debug: results: {results}")
    count = len(results)
    keys = set([k for result in results for k in result.keys()])
    context = {
        'cookies': request.COOKIES,
        'error_message': error_message,
        'count': count,
        'results': results,
        'target_collection': target_collection,
        'query': query_request,
        'keys': keys
    }
    return render(request, 'beacon/phenoclinic_results.html', context)


##################################################
### QUERY HELP
##################################################

def query_help(request):

    context = {
        'cookies': request.COOKIES,
        'error_message': None,
        'results': None,
    }

    return render(request, 'beacon/query_help.html', context)


##################################################
### FILTERING TERMS
##################################################

def filtering_terms(request):

    context = {
        'cookies': request.COOKIES,
        'error_message': None,
        'results': FILTERING_TERMS_DICT,
    }

    return render(request, 'beacon/filtering_terms.html', context)
    

##################################################
### ERRORS
##################################################


def handle_page_not_found(request, exception):

    context = {
        'cookies': request.COOKIES,
        'error_message': "Page not found.",
        'results': '',
    }

    return render(request, 'beacon/error.html', context)
