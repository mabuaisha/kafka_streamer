import sys
import logging
import json

import django.conf
from django.core.management.base import BaseCommand

from confluent_kafka import Consumer, KafkaException, KafkaError

from pubsub import models

logger = logging.getLogger(__name__)

CONFIG = {
    'bootstrap.servers': django.conf.settings.CLOUDKARAFKA_BROKERS,
    'group.id': "%s-consumer" % django.conf.settings.CLOUDKARAFKA_USERNAME,
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
    help = 'OpenStreet Map Kafka Consumer'

    def handle(self, *args, **kwargs):
        c = Consumer(**CONFIG)
        topic = django.conf.settings.CLOUDKARAFKA_TOPIC_OSM
        c.subscribe([topic])
        logger.info('Subscribed to {0} topic \n'.format(topic))
        try:
            while True:
                msg = c.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    # Error or event
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        # End of partition event
                        sys.stderr.write(
                            '{0} [{1}] reached end at offset {2}\n'
                            ''.format(msg.topic(),
                                      msg.partition(),
                                      msg.offset()))
                    elif msg.error():
                        # Error
                        raise KafkaException(msg.error())
                else:
                    osm_item = msg.value()
                    osm_item = osm_item.decode()
                    osm_item = json.loads(osm_item)
                    osm_values = {}
                    for key in OSM_KEYS:
                        value = osm_item.get(key) or ''
                        if key == 'id':
                            key = 'osm_id'
                        osm_values[key] = value

                    osm, created = \
                        models.OpenStreetMap.objects.get_or_create(
                            **osm_values
                        )
                    # If the object is not created
                    if not created:
                        for attr, value in osm_values.items():
                            if attr != 'osm_id':
                                setattr(osm, attr, value or '')
                                osm.save()

                    sys.stderr.write('{0} [{1}] at offset {2}\n'
                                     ''.format(msg.topic(),
                                               msg.partition(),
                                               msg.offset()))
                    logger.info(osm_item)

        except KeyboardInterrupt:
            logger.warning('Aborted by user\n')

        # Close down consumer to commit final offsets.
        c.close()
