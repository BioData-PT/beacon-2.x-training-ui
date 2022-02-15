from django.shortcuts import render
from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import render
import re
import json

from app.utils import get_db_handle, get_collection_handle


##################################################
### DATABASE CONFIG
##################################################

DATABASE_NAME, DATABASE_HOST, DATABASE_PORT, USERNAME, PASSWORD = "beacon", "localhost", "27017", "root", "example"

db_handle, mongo_client = get_db_handle(DATABASE_NAME, DATABASE_HOST, DATABASE_PORT, USERNAME, PASSWORD)


##################################################
### INDEX
##################################################

def index(request):
    display_options = [3,5,10]
    context = {
        'display_options': display_options,
    }
    return render(request, 'beacon/index.html', context)

# def display(request):
#     try:
#         choice = int(request.POST['choice'])
#     except KeyError:
#         display_options = [3,5,10]
#         return render(request, 'beacon/index.html', {
#             'display_options': display_options,
#             'error_message': "You didn't select a choice.",
#         })


#     collection_handle = get_collection_handle(db_handle, "individuals")

#     results = list(collection_handle.find({}).limit(choice))

#     context = {
#         'results': results,
#     }
#     return render(request, 'beacon/results.html', context)

##################################################
### COHORTS
##################################################

def cohorts(request):
    collection_handle = get_collection_handle(db_handle, "cohorts")

    results = list(collection_handle.find({}))
    count = len(results)

    context = {
        'error_message': None,
        'count': count,
        'results': results,
    }

    return render(request, 'beacon/results.html', context)


##################################################
### VARIANT
##################################################

def variant(request):
    context = {
        'error_message': None,
    }
    return render(request, 'beacon/variant.html', context)

def variant_response(request):
    try:
        query = request.POST['query']
    except KeyError:
        error_message = "Error"
        return render(request, 'beacon/variant.html', {
            'error_message': error_message,
        })

    pattern = '^(X|Y|MT|[1-9]|1[0-9]|2[0-2])\s*\:\s*(\d+)\s+([ATCGN]+)\s*\>\s*([ATCGN]+)$'
    m = re.match(pattern, query, re.IGNORECASE)
    if not m:
        error_message = "Error"
        return render(request, 'beacon/variant.html', {
            'error_message': error_message,
        })
    chromosome = m.group(1)
    start = int(m.group(2))
    reference = m.group(3).upper()
    alternate = m.group(4).upper()

    print(f"Query: {chromosome} : {start} {reference} > {alternate}")

    collection_handle = get_collection_handle(db_handle, "genomicVariations")

    results = list(collection_handle.find({"position.refseqId": chromosome, "position.start": start, "referenceBases": reference, "alternateBases": alternate}))
    count = len(results)

    context = {
        'error_message': None,
        'count': count,
        'results': results,
    }

    return render(request, 'beacon/results.html', context)

##################################################
### REGION
##################################################

def region(request):
    context = {
        'error_message': None,
    }
    return render(request, 'beacon/region.html', context)

def region_response(request):
    try:
        query = request.POST['query']
    except KeyError:
        error_message = "Error"
        return render(request, 'beacon/region.html', {
            'error_message': error_message,
        })

    pattern = '^(\d+)\s*:\s*(\d+)$'
    m = re.match(pattern, query, re.IGNORECASE)
    if not m:
        error_message = "Error"
        return render(request, 'beacon/region.html', {
            'error_message': error_message,
        })
    start = int(m.group(1))
    end = int(m.group(2))

    print(f"Query: {start} : {end} ")

    collection_handle = get_collection_handle(db_handle, "genomicVariations")

    results = list(collection_handle.find({"position.start": {"$gte": start}, "position.end": {"$lte":end }}))
    count = len(results)

    context = {
        'error_message': None,
        'count': count,
        'results': results,
    }

    return render(request, 'beacon/results.html', context)

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

def phenoclinic(request):
    context = {
        'error_message': None,
    }
    return render(request, 'beacon/phenoclinic.html', context)


def parse_query(request, schema):
    # separate key-value pairs
    request_list = request.split(" ")
    # info to identidy each key, operator and value
    pattern = '(.+)([=|<|>])(.+)'
    operator_dict = {
        "=": "$eq",
        ">": "$gt",
        "<": "$lt"
    }
    # loop through every key-value pair
    query_list_normal_obj = []
    query_list_array_obj = []
    for element in request_list:
        m = re.match(pattern, element, re.IGNORECASE)
        key = m.group(1)
        value = m.group(3)
        operator = m.group(2)
        
        # detect if value if string or ontology
        key_type = ".id" if ":" in value else ".label"  # useful if object_id_label
        
        # for this UI we assume if the value is float, the key is measurements
        try:
            value= float(value)
            str_operator = operator_dict[operator]
            query_measure = f"{{'measures': {{'$elemMatch': {{'assayCode{key_type}': '{key}',  'measurementValue.value': {{'{str_operator}': {value}}}}}}} }}"
            query_list_array_obj.append(query_measure)
        # if not, we can have object_id_label or simple 
        # NOTICE we ignore array_object_complex or array_object_id_label
        except ValueError:
            if key in schema and schema[key] == "object_id_label":
                query_normal = f"'{key}{key_type}': '{value}'"   
                query_list_normal_obj.append(query_normal)
            elif key in schema and schema[key] == "simple":
                query_normal = f"'{key}': '{value}'"   
                query_list_normal_obj.append(query_normal)
                
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

    return query_json  

def phenoclinic_response(request):
    try:
        target_collection = request.POST['target']
        query_request = request.POST['query']
    except KeyError:
        error_message = "Error"
        return render(request, 'beacon/phenoclinic.html', {
            'error_message': error_message,
        })

    collection_handle = get_collection_handle(db_handle, target_collection)

    schema = INDIVIDUALS_DICT if target_collection == "individuals" else BIOSAMPLES_DICT
    query_json = parse_query(query_request, schema)
    if not query_json:
        error_message = "Something went wrong, please try again."
        return render(request, 'beacon/phenoclinic.html', {
            'error_message': error_message,
        })
    print(f"Query: {target_collection} {query_json} ")
    results = list(collection_handle.find(query_json))
    count = len(results)

    context = {
        'error_message': None,
        'count': count,
        'results': results,
    }
    return render(request, 'beacon/results.html', context)
