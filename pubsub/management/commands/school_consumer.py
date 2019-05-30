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


class Command(BaseCommand):
    help = 'School Kafka Consumer'

    def handle(self, *args, **kwargs):
        c = Consumer(**CONFIG)
        topic = django.conf.settings.CLOUDKARAFKA_TOPIC_SCHOOL
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
                    school_item = msg.value()
                    school_item = school_item.decode()
                    school_item = json.loads(school_item)
                    school_values = {}
                    for key, value in school_item.items():
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

                        school_values[key] = value

                    try:
                        school = models.School.objects.get(
                            school_id=school_values['school_id']
                        )
                        for attr, attr_val in school_values.items():
                            attr_val = attr_val or ''
                            if attr != 'school_id':
                                setattr(school, attr, attr_val)

                        school.save()
                    except models.School.DoesNotExist:
                        models.School.objects.create(**school_values)
                    sys.stderr.write('{0} [{1}] at offset {2}\n'
                                     ''.format(msg.topic(),
                                               msg.partition(),
                                               msg.offset()))
                    logger.info(school_item)

        except KeyboardInterrupt:
            logger.warning('Aborted by user\n')

        # Close down consumer to commit final offsets.
        c.close()
