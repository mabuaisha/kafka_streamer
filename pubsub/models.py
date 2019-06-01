import django.db.models


class OpenStreetMap(django.db.models.Model):
    created_on = django.db.models.DateTimeField(auto_now_add=True)
    updated_on = django.db.models.DateTimeField(auto_now=True)

    osm_id = django.db.models.CharField(max_length=100,
                                        unique=True,
                                        db_index=True)

    latitude = django.db.models.CharField(max_length=100)
    longitude = django.db.models.CharField(max_length=100)
    housenumber = django.db.models.CharField(max_length=100, blank=True)
    amenity = django.db.models.CharField(max_length=250, blank=True)
    name = django.db.models.CharField(max_length=250, blank=True)
    postcode = django.db.models.CharField(max_length=250, blank=True)
    city = django.db.models.CharField(max_length=250, blank=True)
    country = django.db.models.CharField(max_length=250, blank=True)
    street = django.db.models.CharField(max_length=250, blank=True)
    website = django.db.models.CharField(max_length=250, blank=True)
    phone = django.db.models.CharField(max_length=250, blank=True)
    email = django.db.models.CharField(max_length=250, blank=True)
    religion = django.db.models.CharField(max_length=250, blank=True)
    opening_hours = django.db.models.CharField(max_length=250, blank=True)
    internet_access = django.db.models.CharField(max_length=250, blank=True)
    building = django.db.models.CharField(max_length=250, blank=True)
    denomination = django.db.models.CharField(max_length=250,  blank=True)

    class Meta:
        verbose_name_plural = 'OpenStreetMaps'
        verbose_name = 'OpenStreetMap'

    def __unicode__(self):
        return self.osm_id


class GeoName(django.db.models.Model):
    created_on = django.db.models.DateTimeField(auto_now_add=True)
    updated_on = django.db.models.DateTimeField(auto_now=True)

    geoname_id = django.db.models.CharField(max_length=100,
                                            unique=True,
                                            db_index=True)

    osm = django.db.models.ForeignKey(OpenStreetMap,
                                      null=True,
                                      related_name='geonames',
                                      on_delete=django.db.models.CASCADE)

    latitude = django.db.models.CharField(max_length=100)
    longitude = django.db.models.CharField(max_length=100)
    name = django.db.models.CharField(max_length=250, blank=True)
    alt_name = django.db.models.CharField(max_length=250, blank=True)
    country_code = django.db.models.CharField(max_length=250, blank=True)
    location_map = django.db.models.CharField(max_length=250, blank=True)
    feature_class = django.db.models.CharField(max_length=250, blank=True)
    feature_code = django.db.models.CharField(max_length=250, blank=True)
    parent_feature = django.db.models.CharField(max_length=250, blank=True)
    parent_country = django.db.models.CharField(max_length=250, blank=True)
    nearby_features = django.db.models.CharField(max_length=250, blank=True)
    wikipedia_article = django.db.models.CharField(max_length=250, blank=True)

    class Meta:
        verbose_name_plural = 'GeoNames'
        verbose_name = 'GeoNames'

    def __unicode__(self):
        return self.geoname_id


class School(django.db.models.Model):
    created_on = django.db.models.DateTimeField(auto_now_add=True)
    updated_on = django.db.models.DateTimeField(auto_now=True)

    school_id = django.db.models.CharField(max_length=100,
                                           unique=True,
                                           db_index=True)

    osm = django.db.models.ForeignKey(OpenStreetMap,
                                      null=True,
                                      related_name='schools',
                                      on_delete=django.db.models.CASCADE)

    latitude = django.db.models.CharField(max_length=100)
    longitude = django.db.models.CharField(max_length=100)
    latitude27 = django.db.models.CharField(max_length=100, blank=True)
    longitude27 = django.db.models.CharField(max_length=100, blank=True)
    name = django.db.models.CharField(max_length=250, blank=True)
    region = django.db.models.CharField(max_length=250, blank=True)
    gender = django.db.models.CharField(max_length=250, blank=True)
    category = django.db.models.CharField(max_length=250, blank=True)
    location = django.db.models.CharField(max_length=250, blank=True)
    directorate = django.db.models.CharField(max_length=250, blank=True)
    code = django.db.models.CharField(max_length=250, blank=True)

    class Meta:
        verbose_name_plural = 'Schools'
        verbose_name = 'School'

    def __unicode__(self):
        return self.school_id


class WikiEntity(django.db.models.Model):
    created_on = django.db.models.DateTimeField(auto_now_add=True)
    updated_on = django.db.models.DateTimeField(auto_now=True)

    wiki_id = django.db.models.CharField(max_length=100,
                                         unique=True,)

    osm = django.db.models.ForeignKey(OpenStreetMap,
                                      null=True,
                                      related_name='wiki_entities',
                                      on_delete=django.db.models.CASCADE)

    title = django.db.models.CharField(max_length=250, blank=True)
    name = django.db.models.CharField(max_length=250, blank=True)
    description = django.db.models.CharField(max_length=250, blank=True)
    url = django.db.models.CharField(max_length=250, blank=True)
    page_id = django.db.models.CharField(max_length=250, blank=True)
    last_rev_id = django.db.models.CharField(max_length=250, blank=True)
    ns = django.db.models.CharField(max_length=250, blank=True)
    type = django.db.models.CharField(max_length=250, blank=True)
    modified = django.db.models.CharField(max_length=250, blank=True)

    class Meta:
        verbose_name_plural = 'WikiEntities'
        verbose_name = 'WikiEntity'

    def __unicode__(self):
        return self.wiki_id
