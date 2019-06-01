# kafka_streamer

This project use Apache Kafka In order to stream the following data events For Palestine:

 1. OpenStreetMap Data
 2. GeoName Data
 3. WikiData
 4. Schools Data & Location


## Requirements

In order to run this project  you need to install the following tools:

1. Python3

2. [pip3](https://pip.pypa.io/en/stable/installing/) 

3. [pyenv](https://github.com/pyenv/pyenv)

4. [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv)

    `Note`: Make sure to after `pyenv-virtualenv` installation to configure the following to your shell profile:
     
     ```
     eval "$(pyenv init -)"
     eval "$(pyenv virtualenv-init -)"


## Installation

In order to run the application run the following commands:

1. List your installed pythons using the following command `pyenv versions`
   
   ```
    ✗ pyenv versions
      system
   ```
     `Note`: From the above result, there are two versions of python installed `system` which is installed in on the system level

2. Install your Python3 version using `pyenv` if the `system` version is not `python3`. Example: `pyenv install 3.7.0`

3. Create virtualenv using depending on your python version `pyenv virtualenv YOUR_PYTHON_VERSION YOUR_VIRTUALENV_NAME`. Example: `pyenv virtualenv 3.7.0 kafka-streamer`

4. Activate the created virtualenv `pyenv activate kafka-streamer`

5. `pip3 install -r requirements.txt`


## Running Kafka Streamer Project

Before run your application you need to make sure that you have a running Kafka contains the following:

1. Kafka Cluster
2. 1 Broker or more
3. 4 topics
        
        
For this application I'm using [cloudkarafka](https://www.cloudkarafka.com/) Cloud Service

There are some environment variables that need to be set/configure before running the application 

```
export SECRET_KEY=YOUR_DJANGO_SECRET_KEY
export CLOUDKARAFKA_BROKERS=YOUR_BROKER_URL1,YOUR_BROKER_URL2
export CLOUDKARAFKA_USERNAME=YOUR_CLOUDKARAFKA_USERNAME
export CLOUDKARAFKA_PASSWORD=YOUR_CLOUDKARAFKA_PASSWORD
export CLOUDKARAFKA_TOPIC_OSM=YOUR_TOPIC_OSM
export CLOUDKARAFKA_TOPIC_GEONAMES=TOPIC_GEONAMES
export CLOUDKARAFKA_TOPIC_SCHOOL=TOPIC_SCHOOL
export CLOUDKARAFKA_TOPIC_WIKI=TOPIC_WIKI
export DJANGO_SETTINGS_MODULE=YOUR_DJANGO_SETTINGS
```

### DashBoard Application

This part is simply a `django` project and in order to run the server you need to do the following:

1. Activate your python environment `pyenv activate kafka-streamer`
2. Run `migrate` command `python3 manange.py migrate`
3. Create `superuser` `python3 manange.py createsuperuser`
4. Run development server `python3 manange.py runserver 127.0.0.1:8000`


### Consumers Applications

Consumers are simply django management commands that listen to the Kafka Cluster and process stream data

1. Activate your python environment `pyenv activate kafka-streamer`
2. Run OpenStreetMap Consumer command `python3 manange.py osm_consumer`
3. Run GeoName Consumer command `python3 manange.py geonames_consumer`
4. Run WikiData Consumer command `python3 manange.py school_consumer`
5. Run School Consumer command `python3 manange.py wiki_consumer`


### Producers Applications

Producers are simply django management commands that process data from different data source and then publish them to Kafka Cluster

1. Activate your python environment `pyenv activate kafka-streamer`
2. Run OpenStreetMap Consumer command `python3 manange.py osm_consumer`
3. Run GeoName Consumer command `python3 manange.py geonames_consumer`
4. Run WikiData Consumer command `python3 manange.py school_consumer`
5. Run School Consumer command `python3 manange.py wiki_consumer`