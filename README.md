# Beacon v2 RI - Training UI

## Introduction
The aim of this repository is to host the code and data that will allow anyone to light a [v2 Beacon](https://b2ri-documentation.readthedocs.io/en/latest/what_is_beacon/) and test it.  

To be able to light this beacon, we provide instructions to create a MongoDB instance, to load it with synthetic data from the [CINECA project](https://www.cineca-project.eu/cineca-synthetic-datasets) and to build the Django app with the beacon.  

## Repo organization
- `Dockerfile` and `docker-compose.yml`: Docker files requiered to build the DB and the Beacon.
- `/db`: data and code to load the MongoDB.
- `/app`: Django application, the code of the Beacon.


## Deploying the beacon
For deploying we need Docker and Docker Compose, so make sure you have them installed. 

The beacon is based on three containers:  
- The DB
- The DB data loader
- The Django app

For the beacon to properly work, the DB container has to be up and running. Then the loading container has to be up and load the data (which should last less than 1 minute), when the loading is completed, this container will exit. Finally, the web container has to be up and running.  

In the root of the repository do:
```
docker-compose up -d
```
This will trigger the build of the DB, the load of the data and the build of the Beacon web app, the latter with a sleeping time of 60s to give time to the loading step.  
As said above, the container that loads the data will exit once the loading is completed, so when you do `docker-compose ps` and see this container's status as `Exit`, it is expected:
```
                 Name                               Command               State             Ports          
-----------------------------------------------------------------------------------------------------------
b2ri_mongodb_training_db-beacon-load_1   docker-entrypoint.sh bash  ...   Exit 0                           
b2ri_mongodb_training_db-beacon_1        docker-entrypoint.sh mongod      Up       0.0.0.0:27018->27017/tcp
b2ri_mongodb_training_web_1              python app/manage.py runse ...   Up       0.0.0.0:8080->8080/tcp  
```

If the web container has also an `Exit` as status, it could be that the waiting time of 60s has not been enough and the web started before the DB was loaded. If this is the case, make sure the DB container is up and the loading container has exitted, then run (and wait 60s):
```
docker-compose restart web
```

Checkout the web logs with `docker-compose logs -f web`. 

```
Attaching to b2ri_mongodb_training_web_1
web_1             | sleep for 60sec
web_1             | Watching for file changes with StatReloader
web_1             | Performing system checks...
web_1             | 
web_1             | System check identified no issues (0 silenced).
web_1             | March 15, 2022 - 17:34:11
web_1             | Django version 3.2.12, using settings 'app.settings'
web_1             | Starting development server at http://0.0.0.0:8080/
web_1             | Quit the server with CONTROL-C.
```

After the 60s of sleep time, the web app will boot, then just go to `localhost:8080/` on your browser.  

## Using the beacon
This Beacon has four main __query pages__:  
- __Variants__: perform SNP queries.
- __Region__: perform range queries by start position.
- __Phenoclinic__: perform queries on the biosamples and individuals collections based on the [schema terms](http://docs.genomebeacons.org/schemas-md/individuals_defaultSchema/), leveraging them together with the filtering terms (values that are understood by that Beacon). 
- __Cohorts__: explore the information about the cohorts that are in this Beacon.

Every query displays the __results__ in three different ways:  
- __Boolean__: Yes and No answer only.
- __Counts__: number of results (controlled/private).
- __Full__: full information about the results (controlled/private).


It also has a dummy log in system that depics the controlled/private visualization of the results.  

### Example queries
- Variant
  - `22 : 16050677 C > T`
- Region
  - `22 : 16050310 - 16050740`   
- Phenoclinic
  - `Individuals` and `ethnicity=NCIT:C16352, geographicOrigin=England, Weight>50, Height-standing>150`
  - `Individuals` and `Weight=98.7828, Height-standing=187.4031`
  - `Individuals` and `ethnicity=NCIT:C16352, England, diseases.diseaseCode.label=asthma`
  - `Individuals` and `ethnicity=NCIT:C16352, female`
  - `Biosamples` and `blood`
  - `Biosamples` and `individualId=HG00096`

\*_Notice multiple key-value pairs need to be comma-separated._