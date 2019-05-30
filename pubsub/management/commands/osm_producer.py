# Standard Imports
import os
import json
import logging
import xml.etree.ElementTree as ET


# Third Imports
import django.conf
from django.core.management.base import BaseCommand
from confluent_kafka import Producer

logger = logging.getLogger(__name__)

BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
WEST_BANK_PATH = os.path.join(BASE_PATH, 'data/westbank/westbank.xml')
GAZA_PATH = os.path.join(BASE_PATH, 'data/gaza/gaza.xml')
OSM_ONTOLOGY = '{https://raw.githubusercontent.com/' \
               'birzeitknowledgegraph-2019/Ontology/master/osm_v2.rdf#}'

CONFIG = {
    'bootstrap.servers': django.conf.settings.CLOUDKARAFKA_BROKERS,
    'session.timeout.ms': django.conf.settings.CLOUDKARAFKA_TIMEOUT,
    'default.topic.config': django.conf.settings.CLOUDKARAFKA_TOPIC_CONFIG,
    'security.protocol': django.conf.settings.CLOUDKARAFKA_PROTOCOL,
    'sasl.mechanisms': django.conf.settings.CLOUDKARAFKA_MECHANISMS,
    'sasl.username': django.conf.settings.CLOUDKARAFKA_USERNAME,
    'sasl.password': django.conf.settings.CLOUDKARAFKA_PASSWORD,
}

OSM_KEYS = (
    'id',
    'latitude',
    'longitude',
    'housenumber',
    'amenity',
    'name',
    'postcode',
    'city',
    'country',
    'street',
    'website',
    'phone',
    'email',
    'religion',
    'opening_hours',
    'internet_access',
    'building',
    'denomination',
)


class Command(BaseCommand):
    help = 'OpenStreet Map Kafka Producer'

    def get_osm_items(self, root):
        for child in root.iter(
                '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description'):
            osm_object = {}

            for key in OSM_KEYS:
                value = '{0}{1}'.format(OSM_ONTOLOGY, key)
                elem = child.find(value)
                elem = elem[0] if isinstance(elem, list) else elem
                if elem is not None:
                    osm_object[key] = elem.text
            yield osm_object

    def publish_osm(self):
        p = Producer(**CONFIG)
        for source_path in [GAZA_PATH, WEST_BANK_PATH]:
            tree = ET.parse(source_path)
            root = tree.getroot()
            for item in self.get_osm_items(root):
                logger.info(item)
                try:
                    p.produce(
                        topic=django.conf.settings.CLOUDKARAFKA_TOPIC_OSM,
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
        self.publish_osm()
