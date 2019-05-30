# Standard Imports
import os
import json
import logging
import xml.etree.ElementTree as ET


# Third Imports
import django.conf
from django.core.management.base import BaseCommand
from confluent_kafka import Producer

# Local imports
from school_mapper import SCHOOL_OSM_MAP

logger = logging.getLogger(__name__)

BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
SCHOOL_PATH = os.path.join(BASE_PATH, 'data/school/data.xml')
SCHOOL_ONTOLOGY = '{https://raw.githubusercontent.com/' \
                  'SoftwareConstructionQMM/' \
                  'DataEngineering/master/GCI-Education.rdf#}'

CONFIG = {
    'bootstrap.servers': django.conf.settings.CLOUDKARAFKA_BROKERS,
    'session.timeout.ms': django.conf.settings.CLOUDKARAFKA_TIMEOUT,
    'default.topic.config': django.conf.settings.CLOUDKARAFKA_TOPIC_CONFIG,
    'security.protocol': django.conf.settings.CLOUDKARAFKA_PROTOCOL,
    'sasl.mechanisms': django.conf.settings.CLOUDKARAFKA_MECHANISMS,
    'sasl.username': django.conf.settings.CLOUDKARAFKA_USERNAME,
    'sasl.password': django.conf.settings.CLOUDKARAFKA_PASSWORD,
}

SCHOOL_KEYS = (
    'has_Lat',
    'has_Long',
    'has_Region',
    'school_Gender',
    'school_Type',
    'has_Lat27',
    'has_Long27',
    'has_Location',
    'has_Directorate',
    'has_Id',
    'has_Name',
    'has_CodeID',
)

SCHOOL_MAPS = {
    'has_Lat': 'latitude',
    'has_Long': 'longitude',
    'has_Region': 'region',
    'school_Gender': 'gender',
    'school_Type': 'category',
    'has_Lat27': 'latitude27',
    'has_Long27': 'longitude27',
    'has_Location': 'location',
    'has_Directorate': 'directorate',
    'has_Id': 'school_id',
    'has_Name': 'name',
    'has_CodeID': 'code'
}


class Command(BaseCommand):
    help = 'School Kafka Producer'

    def get_school_items(self, root):
        for child in root.iter(
                '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description'):
            school_object = {}

            for key in SCHOOL_KEYS:
                value = '{0}{1}'.format(SCHOOL_ONTOLOGY, key)
                elem = child.find(value)
                elem = elem[0] if isinstance(elem, list) else elem
                if elem is not None:
                    if elem.text:
                        school_object[SCHOOL_MAPS[key]] = elem.text

                    osm_id = SCHOOL_OSM_MAP.get(
                        'http://www.mohe.ps/Schools/{0}'.format(elem.text))
                    if osm_id:
                        school_object['osm_id'] = osm_id
            yield school_object

    def publish_schools(self):
        p = Producer(**CONFIG)
        tree = ET.parse(SCHOOL_PATH)
        root = tree.getroot()
        for item in self.get_school_items(root):
            logger.info(item)
            try:
                p.produce(
                    topic=django.conf.settings.CLOUDKARAFKA_TOPIC_SCHOOL,
                    value=str(json.dumps(item)),
                    callback=self.delivery_callback)
            except BufferError as e:
                logger.error('Local producer queue is full '
                             '({0} messages awaiting delivery):'
                             ' try again\n'.format(len(p)))
            p.poll(0)

        logger.info('Waiting for {0} deliveries\n'.format(len(p)))
        p.flush()

    @staticmethod
    def delivery_callback(err, msg):
        if err:
            logger.error('Message failed delivery: {0}\n'.format(err))
        else:
            logger.info('Message delivered to {0} {1}\n'
                        ''.format(msg.topic(), msg.partition()))

    def handle(self, *args, **kwargs):
        self.publish_schools()
