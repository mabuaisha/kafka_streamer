import sys
import logging
import json

from django.core.management.base import BaseCommand
import django.conf

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


GEONAMES_KEYS = (
    'geoname_id',
    'osm_id',
    'latitude',
    'longitude',
    'name',
    'alt_name',
    'country_code',
    'location_map',
    'feature_class',
    'feature_code',
    'parent_feature',
    'parent_country',
    'nearby_features',
    'wikipedia_article'
)


class Command(BaseCommand):
    help = 'GeoNames Kafka Consumer'

    def handle(self, *args, **kwargs):
        c = Consumer(**CONFIG)
        topic = django.conf.settings.CLOUDKARAFKA_TOPIC_GEONAMES
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
                    geoname_item = msg.value()
                    geoname_item = geoname_item.decode()
                    geoname_item = json.loads(geoname_item)
                    geoname_values = {}
                    for key, value in geoname_item.items():
                        if key == 'osm_id':
                            try:
                                osm_rel = \
                                    models.OpenStreetMap.objects.get(
                                        osm_id=value
                                    )
                                value = osm_rel.id
                            except models.OpenStreetMap.DoesNotExist:
                                value = None

                        if key == 'osm_id' and not value:
                            continue

                        geoname_values[key] = value

                    try:
                        geoname = models.GeoName.objects.get(
                            geoname_id=geoname_values['geoname_id']
                        )
                        for attr, attr_val in geoname_values.items():
                            attr_val = attr_val or ''
                            if attr != 'geoname_id':
                                setattr(geoname, attr, attr_val)

                        geoname.save()
                    except models.GeoName.DoesNotExist:
                        logger.info('Print GeoNames {0}'.format(geoname_values))
                        models.GeoName.objects.create(**geoname_values)

                    sys.stderr.write('{0} [{1}] at offset {2}\n'
                                     ''.format(msg.topic(),
                                               msg.partition(),
                                               msg.offset()))
                    logger.info(geoname_item)

        except KeyboardInterrupt:
            logger.warning('Aborted by user\n')

        # Close down consumer to commit final offsets.
        c.close()
