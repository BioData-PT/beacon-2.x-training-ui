from django.shortcuts import render
from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import render
import re
import json
import os

from app.utils import get_db_handle, get_collection_handle


##################################################
### DATABASE CONFIG
##################################################

# Get environment variables or use default
DATABASE_NAME = os.getenv('DATABASE_NAME', 'beacon')
DATABASE_HOST = os.getenv('DATABASE_HOST', 'localhost')
DATABASE_PORT = os.getenv('DATABASE_PORT', '27017')
USERNAME = os.getenv('USERNAME', 'root')
PASSWORD = os.getenv('PASSWORD', 'example')

db_handle, mongo_client = get_db_handle(DATABASE_NAME, DATABASE_HOST, DATABASE_PORT, USERNAME, PASSWORD)

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
### INDEX
##################################################

def index(request):
    display_options = [3,5,10]
    context = {
        'display_options': display_options,
    }
    return render(request, 'beacon/index.html', context)


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
        }
        return render(request, 'beacon/cohorts_results.html', context)

    context = {
        'error_message': None,
        'count': count,
        'results': results,
        'keys': keys
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

    collection_handle = get_collection_handle(db_handle, "genomicVariations")

    results = list(collection_handle.find({"position.refseqId": chromosome, "position.start": start, "referenceBases": reference, "alternateBases": alternate}))
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

    pattern = '^(\d+)\s*:\s*(\d+)$'
    m = re.match(pattern, query, re.IGNORECASE)
    if not m:
        error_message = "The query pattern is wrong. Please, use 'start : end' and try again."
        return render(request, 'beacon/region_results.html', {
            'cookies': request.COOKIES,
            'error_message': error_message,
            'query': query
        })
    start = int(m.group(1))
    end = int(m.group(2))

    print(f"Query: {start} : {end} ")

    collection_handle = get_collection_handle(db_handle, "genomicVariations")

    results = list(collection_handle.find({"position.start": {"$gte": start}, "position.end": {"$lte":end }}))
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

FILTERING_TERMS_DICT = {
    "female": ("individuals", "sex"),
    "male": ("individuals", "sex"),
    "blood": ("biosamples", "sampleOriginType")
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
            key = m.group(1)
            value = m.group(3)
            operator = m.group(2)
        except:
            if element in FILTERING_TERMS_DICT.keys():
                key = FILTERING_TERMS_DICT[element][1]
                value = element
                operator = "="
            else:
                # this filtering term is not registered
                error = "Some of the query terms are incorrect/not available. Please, check the schema, the filtering terms and the query syntax and try again."
                continue
        
        # detect if value if string or ontology
        key_type = ".id" if ":" in value else ".label"  # useful if object_id_label
        
        # for this UI we assume if the value is float, the key is measurements
        try:
            value= float(value)
            str_operator = operator_dict[operator]
            # control cases where the user didn't put commas in the query
            if not key.startswith(tuple(schema.keys())):
                query_measure = f"{{'measures': {{'$elemMatch': {{'assayCode{key_type}': '{key}',  'measurementValue.value': {{'{str_operator}': {value}}}}}}} }}"
                query_list_array_obj.append(query_measure)
            else:
                error = "Some of the query terms are incorrect/not available. Please, check the schema, the filtering terms and the query syntax and try again."
        # if not, we can have object_id_label or simple 
        # NOTICE we ignore array_object_complex or array_object_id_label
        except ValueError:
            if key in schema and schema[key] == "object_id_label":
                query_normal = f"'{key}{key_type}': '{value}'"   
                query_list_normal_obj.append(query_normal)
            elif key in schema and schema[key] == "simple":
                query_normal = f"'{key}': '{value}'"   
                query_list_normal_obj.append(query_normal)
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