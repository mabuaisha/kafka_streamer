# Standard Imports
import os
import json
import logging
import xml.etree.ElementTree as ET


# Third Imports
import django.conf
from django.core.management.base import BaseCommand
from confluent_kafka import Producer

# Local Imports
from geo_mapper import GEO_MAP

logger = logging.getLogger(__name__)

BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
GEO_PATH = os.path.join(BASE_PATH, 'data/geonames/palestine.xml')


CONFIG = {
    'bootstrap.servers': django.conf.settings.CLOUDKARAFKA_BROKERS,
    'session.timeout.ms': django.conf.settings.CLOUDKARAFKA_TIMEOUT,
    'default.topic.config': django.conf.settings.CLOUDKARAFKA_TOPIC_CONFIG,
    'security.protocol': django.conf.settings.CLOUDKARAFKA_PROTOCOL,
    'sasl.mechanisms': django.conf.settings.CLOUDKARAFKA_MECHANISMS,
    'sasl.username': django.conf.settings.CLOUDKARAFKA_USERNAME,
    'sasl.password': django.conf.settings.CLOUDKARAFKA_PASSWORD,
}

GEONAMES_MAP = {
    'name': '{http://www.geonames.org/ontology#}name',
    'alt_name': '{http://www.geonames.org/ontology#}alternateName',
    'lat': '{http://www.w3.org/2003/01/geo/wgs84_pos#}lat',
    'long': '{http://www.w3.org/2003/01/geo/wgs84_pos#}long',
    'countryCode': '{http://www.geonames.org/ontology#}countryCode',
    'locationMap': '{http://www.geonames.org/ontology#}locationMap',
    'featureClass': '{http://www.geonames.org/ontology#}featureClass',
    'featureCode': '{http://www.geonames.org/ontology#}featureCode',
    'parentFeature': '{http://www.geonames.org/ontology#}parentFeature',
    'parentCountry': '{http://www.geonames.org/ontology#}parentCountry',
    'nearbyFeatures': '{http://www.geonames.org/ontology#}nearbyFeatures',
    'wikipediaArticle': '{http://www.geonames.org/ontology#}wikipediaArticle',

}

GEONAMES_RESOURCE = (
    'location_map',
    'feature_class',
    'feature_code',
    'parent_country',
    'parent_feature',
    'nearby_features',
    'wikipedia_article',
)

GEONAME_KEYS_MAP = {
    'lat': 'latitude',
    'long': 'longitude',
    'countryCode': 'country_code',
    'locationMap': 'location_map',
    'featureClass': 'feature_class',
    'featureCode': 'feature_code',
    'parentCountry': 'parent_country',
    'parentFeature': 'parent_feature',
    'nearbyFeatures': 'nearby_features',
    'wikipediaArticle': 'wikipedia_article'
}


class Command(BaseCommand):
    help = 'GeoNames Kafka Producer'

    def get_geonames(self, root):
        inverted_geo = dict(map(reversed, GEO_MAP.items()))
        for child in root.iter('{http://www.geonames.org/ontology#}Feature'):
            geo_object = {}
            geo_id = child.attrib[
                '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about']

            if inverted_geo.get(geo_id):
                osm_id = inverted_geo[geo_id]
                geo_object['osm_id'] = osm_id

            geoname_id = geo_id.split('/')[-2]
            geo_object['geoname_id'] = geoname_id
            for key, value in GEONAMES_MAP.items():
                elem = child.find(value)
                elem = elem[0] if isinstance(elem, list) else elem
                if elem is not None:
                    geo_key = GEONAME_KEYS_MAP.get(key) or key
                    if geo_key not in GEONAMES_RESOURCE:
                        geo_object[geo_key] = elem.text
                    else:
                        geo_object[geo_key] = \
                            elem.attrib['{http://www.w3.org/' \
                                        '1999/02/22-rdf-syntax-ns#}resource']
            yield geo_object

    def publish_geo_names(self):
        p = Producer(**CONFIG)
        tree = ET.parse(GEO_PATH)
        root = tree.getroot()
        for item in self.get_geonames(root):
            logger.info(item)
            try:
                p.produce(
                    topic=django.conf.settings.CLOUDKARAFKA_TOPIC_GEONAMES,
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
        self.publish_geo_names()
