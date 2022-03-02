# Beacon v2 RI - Training UI

## Introduction
The aim of this repository is to host the code and data that will allow anyone to light a [v2 Beacon](https://b2ri-documentation.readthedocs.io/en/latest/what_is_beacon/) and test it.  

To be able to light this beacon, we provide instructions to create a MongoDB instance, to load it with synthetic data from the [CINECA project](https://www.cineca-project.eu/cineca-synthetic-datasets) and to build the Django app with the beacon.  

## Repo organization
- `Dockerfile` and `docker-compose.yml`: Docker files requiered to build the DB and the Beacon.
- `/db`: data and code to load the MongoDB.
- `/app`: Django application, the code of the Beacon.


## Deploying the beacon
For deploying we need Docker and Docker Compose , so make sure you have them installed. 
In the root of the repository do:
```
docker-compose up -d
```
This will trigger the build of the DB, the load of the data and the build of the Beacon app, each of them on their own Docker container. The container that loads the data will exit once the loading is completed, so when you do `docker-compose ps` and see this container's status as `Exit 0`, everything should be ready:
```
                 Name                               Command               State             Ports          
-----------------------------------------------------------------------------------------------------------
b2ri_mongodb_training_db-beacon-load_1   docker-entrypoint.sh bash  ...   Exit 0                           
b2ri_mongodb_training_db-beacon_1        docker-entrypoint.sh mongod      Up       0.0.0.0:27018->27017/tcp
b2ri_mongodb_training_web_1              python app/manage.py runse ...   Up       0.0.0.0:8080->8080/tcp  
```

Then, just go to `localhost:8080/` on your browser. 

## Using the beacon
This Beacon has four main __query pages__:  
- __Variants__: perform SNP queries.
- __Region__: perform range queries by start position.
- __Phenoclinic__: perform queries on the biosamples and individuals collections based on the [schema terms](https://beacon-schema-2.readthedocs.io/en/latest/schemas-md/individuals_defaultSchema/), leveraging them together with the filtering terms (values that are understood by that Beacon). 
- __Cohorts__: explore the information about the cohorts that are in this Beacon.

Every query displays the __results__ in three different ways:  
- __Boolean__: Yes and No answer only.
- __Counts__: number of results (controlled/private).
- __Full__: full information about the results (controlled/private).


It also has a dummy log in system that depics the controlled/private visualization of the results.  
