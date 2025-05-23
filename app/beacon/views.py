from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.http import Http404
from django.utils.datastructures import MultiValueDictKeyError
import re
import json
import os
import requests
import logging

from app.schemas import INDIVIDUALS_DICT, BIOSAMPLES_DICT, FILTERING_TERMS_DICT
from app.utils import get_cohort_query, get_db_handle, get_collection_handle, get_payload_default, get_region_query, get_variant_query, parse_query, parse_query_api
from app.utils import get_response_data

##################################################
### DATABASE CONFIG
##################################################

# Get environment variables or use default
DATABASE_NAME = os.getenv('DATABASE_NAME', 'beacon')
DATABASE_HOST = os.getenv('DATABASE_HOST', 'mongo')
DATABASE_PORT = os.getenv('DATABASE_PORT', '27017')
BEACON_PROT = os.getenv('BEACON_PROT', 'http') # could be https
BEACON_HOST = os.getenv('BEACON_HOST', 'beacon')
BEACON_PORT = os.getenv('BEACON_PORT', '5050')
BEACON_LOCATION = os.getenv('BEACON_LOCATION', '/api/')
USERNAME = os.getenv('USERNAME', 'root')
PASSWORD = os.getenv('PASSWORD', 'example')

BEACON_URL = url = f"{BEACON_PROT}://{BEACON_HOST}:{BEACON_PORT}{BEACON_LOCATION}"

db_handle, mongo_client = get_db_handle(DATABASE_NAME, DATABASE_HOST, DATABASE_PORT, USERNAME, PASSWORD)

#print(f"\nConnecting to {DATABASE_HOST}:{DATABASE_PORT} {DATABASE_NAME} as {USERNAME}")



##################################################
### COHORTS
##################################################

def cohorts(request):
    return cohorts_api(request)


def cohorts_db(request):
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

def cohorts_api(request):

    query_json, error_message = get_cohort_query()
    route = "cohorts"
    url = f"{BEACON_URL}{route}"
    
    payload = query_json
    
        
    try:
        # query the API
        response = requests.post(url=url, json=payload).json()
        # results = response['response']['resultSets'][0]['results']
        results = response['response']['collections']
    except Exception as e:
        error_message = "Something went wrong while trying to access the API, please try again."
        logging.error(f"Error while accessing API: {e}")
        
        return render(request, 'beacon/variant_results.html', {
            'cookies': request.COOKIES,
            'error_message': error_message,
            'count': 0,
            'exists': False,
            'results': [],
        })
    
    # cohorts have different result format
    count = response['responseSummary']['numTotalResults']
    
    keys = set()
    if len(results):
        keys = set([k for result in results for k in result.keys()])
    
    context = {
        'error_message': None,
        'cookies': request.COOKIES,
        #'exists': exists,
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
    return variant_response_API(request)

def variant_response_DB(request):
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

def variant_response_API(request):
        
    try:
        # debug prints
        logging.info(f"Request: {request.POST}")
        # =================
        
        query_request = request.POST['query']
    except KeyError as ex:
        error_message = "Something went wrong with the request, please try again."
        logging.error(error_message + f" Exception: {ex}")
        return render(request, 'beacon/variant_results.html', {
            'cookies': request.COOKIES,
            'error_message': error_message,
            'exists': False,
            'count': 0,
            'results': [],
            'query': "",
        })

    query_json, error_message = get_variant_query(query_request)
    if not query_json:
        error_message = "Something went wrong while parsing the query: " + error_message
        return render(request, 'beacon/variant_results.html', {
            'cookies': request.COOKIES,
            'error_message': error_message,
            'count': 0,
            'results': [],
            'query': query_request,
        })
    print(f"Query: {query_json}")
    
    route = "g_variants"
    url = f"{BEACON_URL}{route}/"
    
    payload = query_json
    
    
    logging.info(f"Debug: payload: {payload}")
    logging.info(f"Debug: URL = {url}")
    
    try:
        # query the API
        headers = {
            'Content-type': 'application/json',
            'Authorization': request.COOKIES.get('Authorization')
        }
        logging.debug(f"Debug: headers: {headers}")
        response = requests.post(url=url, json=payload, headers=headers).json()
        logging.debug(f"Debug: response: {response}")
        results = response['response']['resultSets'][0]['results']
    except Exception as e:
        error_message = "Something went wrong while trying to access the API, please try again."
        logging.error(f"Error while accessing API: {e}")
        
        return render(request, 'beacon/variant_results.html', {
            'cookies': request.COOKIES,
            'error_message': error_message,
            'count': 0,
            'results': [],
            'query': query_request,
        })
    
    
    #logging.info(f"Debug: results: {results}")
    #count = response['response']['resultSets'][0]['resultsCount']
    exists, count, results = get_response_data(response)
    logging.debug("Debug: count: " + str(count))
    
    keys = set()
    if len(results):
        keys = set([k for result in results for k in result.keys()])
    context = {
        'error_message': None,
        'cookies': request.COOKIES,
        'exists': exists,
        'count': count,
        'results': results,
        'query': query_request,
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
    return region_response_API(request)

def region_response_API(request):
        
    try:
        # debug prints
        logging.info(f"Request: {request.POST}")
        # =================
        
        query_request = request.POST['query']
    except KeyError as ex:
        error_message = "Something went wrong with the request, please try again."
        logging.error(error_message + f" Exception: {ex}")
        return render(request, 'beacon/region.html', {
            'cookies': request.COOKIES,
            'error_message': error_message,
            'exists': False,
            'count': 0,
            'results': [],
            'query': "",
        })

    query_json, error_message = get_region_query(query_request)
    if not query_json:
        error_message = "Something went wrong while parsing the query: " + error_message
        return render(request, 'beacon/region.html', {
            'cookies': request.COOKIES,
            'error_message': error_message,
            'exists': False,
            'count': 0,
            'results': [],
            'query': query_request,
        })
    print(f"Query: {query_json} ")
    
    route = "g_variants"
    url = f"{BEACON_URL}{route}/"
    
    payload = query_json
    
    
    logging.info(f"Debug: payload: {payload}")
    logging.info(f"Debug: URL = {url}")
    
    try:
        # query the API
        headers = {
            'Content-type': 'application/json',
            'Authorization': request.COOKIES.get('Authorization')
        }
        response = requests.post(url=url, json=payload, headers=headers).json()
        results = response['response']['resultSets'][0]['results']
    except Exception as e:
        error_message = "Something went wrong while trying to access the API, please try again."
        logging.error(f"Error while accessing API: {e}")
        
        return render(request, 'beacon/region.html', {
            'cookies': request.COOKIES,
            'error_message': error_message,
            'exists': False,
            'count': 0,
            'results': [],
            'query': query_request,
        })
    
    
    #logging.info(f"Debug: results: {results}")
    #count = response['response']['resultSets'][0]['resultsCount']
    exists, count, results = get_response_data(response)
    logging.debug("Debug: count: " + str(count))
    
    keys = set()
    if len(results):
        keys = set([k for result in results for k in result.keys()])
    context = {
        'error_message': None,
        'cookies': request.COOKIES,
        'exists': exists,
        'count': count,
        'results': results,
        'query': query_request,
        'keys': keys
    }
    return render(request, 'beacon/region_results.html', context)

def region_response_DB(request):
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



def phenoclinic(request):
    context = {
        'cookies': request.COOKIES,
        'error_message': None,
    }
    return render(request, 'beacon/phenoclinic.html', context)

def phenoclinic_response(request):
    # choose which method to use
    
    #return phenoclinic_response_DB(request)
    return phenoclinic_response_API(request)

# NOT USED ANYMORE
def phenoclinic_response_DB(request):
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


# USING API
def phenoclinic_response_API(request: HttpRequest):
    
    try:
        # debug prints
        logging.info(f"Request: {request.POST}")
        # =================
        
        target_collection = request.POST['target']
        query_request = request.POST['query']
        
    except MultiValueDictKeyError as ex:
        error_message = "Something went wrong with the request, please try again."
        logging.error(error_message + f" Exception: {ex}")
        return render(request, 'beacon/phenoclinic_results.html', {
            'cookies': request.COOKIES,
            'error_message': error_message,
            # avoids crash when target_collection is not defined
            # 'target_collection': target_collection, 
            # 'query': query_request
        })


    query_json, error_message = parse_query_api(query_request)
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
    
    route = "individuals" if target_collection == "individuals" else "biosamples"
    url = f"{BEACON_URL}{route}/"
    
    payload = query_json
    
    
    logging.info(f"Debug: payload: {payload}")
    logging.info(f"Debug: URL = {url}")
    
    try:
        # query the API
        headers = {
            'Content-type': 'application/json',
            'Authorization': request.COOKIES.get('Authorization')
        }
        response = requests.post(url=url, json=payload, headers=headers).json()
        results = response['response']['resultSets'][0]['results']
    except Exception as e:
        error_message = "Something went wrong while trying to access the API, please try again."
        logging.error(f"Error while accessing API: {e}")
        
        return render(request, 'beacon/phenoclinic_results.html', {
        'cookies': request.COOKIES,
        'error_message': error_message,
        'target_collection': target_collection,
        'query': query_request
    })
    
    
    #logging.info(f"Debug: results: {results}")
    #count = response['response']['resultSets'][0]['resultsCount']
    exists, count, results = get_response_data(response)
    logging.debug("Debug: exists: " + str(exists))
    logging.debug("Debug: count: " + str(count))
    
    keys = set()
    if len(results):
        keys = set([k for result in results for k in result.keys()])
    context = {
        'cookies': request.COOKIES,
        'error_message': error_message,
        'exists': exists,
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
### API HELP
##################################################

def api_help(request):
    
    return render(request, 'beacon/api_help.html')    

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
