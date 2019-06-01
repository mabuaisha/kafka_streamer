# Standard Imports
import os
import json
import requests
import logging


# Third Imports
import django.conf
from django.core.management.base import BaseCommand
from confluent_kafka import Producer

# Local imports
from wiki_mapper import WIKI_OSM_MAP

logger = logging.getLogger(__name__)

CONFIG = {
    'bootstrap.servers': django.conf.settings.CLOUDKARAFKA_BROKERS,
    'session.timeout.ms': django.conf.settings.CLOUDKARAFKA_TIMEOUT,
    'default.topic.config': django.conf.settings.CLOUDKARAFKA_TOPIC_CONFIG,
    'security.protocol': django.conf.settings.CLOUDKARAFKA_PROTOCOL,
    'sasl.mechanisms': django.conf.settings.CLOUDKARAFKA_MECHANISMS,
    'sasl.username': django.conf.settings.CLOUDKARAFKA_USERNAME,
    'sasl.password': django.conf.settings.CLOUDKARAFKA_PASSWORD,
}


WIKI_API = 'https://www.wikidata.org/w/api.php?' \
           'action=wbgetentities&ids={0}&format=json'


WIKI_RESOURCE_KEYS = (
    'pageid',
    'ns',
    'title',
    'lastrevid',
    'type',
    'modified',
    'labels',
    'descriptions'
)


WIKI_LANGS = (
    'en',
    'fr'
)

WIKI_MAP_KEYS = {
    'pageid': 'page_id',
    'lastrevid': 'last_rev_id',
}


class Command(BaseCommand):
    help = 'Wiki Kafka Producer'

    def get_wiki_items(self):
        for key, value in WIKI_OSM_MAP.items():
            wiki_object = {}
            res = requests.get(WIKI_API.format(key))
            wiki_entities = json.loads(res.content)
            entities = wiki_entities.get('entities')
            wiki_resource = entities.get(key)
            wiki_object['wiki_id'] = key
            wiki_object['osm_id'] = value
            wiki_object['url'] = 'https://wikidata.org/entity/{0}'.format(key)
            for wiki_key, wiki_value in wiki_resource.items():
                if wiki_key in WIKI_RESOURCE_KEYS:
                    if wiki_key not in ['labels', 'descriptions']:
                        wiki_key = WIKI_MAP_KEYS.get(wiki_key, wiki_key)
                        wiki_object[wiki_key] = str(wiki_value)
                    else:
                        for item in WIKI_LANGS:
                            lan = wiki_value.get(item)
                            if lan:
                                label = lan['value']
                                if wiki_key == 'labels':
                                    wiki_object['name'] = label
                                else:
                                    wiki_object['description'] = label
                                break

            yield wiki_object

    def publish_wiki(self):
        p = Producer(**CONFIG)
        for item in self.get_wiki_items():
            logger.info(item)
            try:
                p.produce(
                    topic=django.conf.settings.CLOUDKARAFKA_TOPIC_WIKI,
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
        self.publish_wiki()
