import django.contrib.admin

from . import models


@django.contrib.admin.register(models.OpenStreetMap)
class OpenStreetMapAdmin(django.contrib.admin.ModelAdmin):
    list_display = ('osm_id', 'latitude',
                    'longitude', 'name',
                    'country', 'postcode',
                    'city', 'street',
                    'phone', 'email',)

    search_fields = ('osm_id', 'latitude',
                     'longitude', 'postcode',
                     'city', 'country')
    ordering = ('-created_on', )
    fieldsets = (
        ('Status', {
            'fields': ('created_on', 'updated_on', 'osm_id', ),
        }),
        ('Geo Location Information', {
            'fields': ('latitude', 'longitude',),
        }),
        ('Address Information', {
            'fields': ('country', 'city',
                       'postcode', 'street',
                       'phone', 'email'),
        }),
        ('Others', {
            'fields': ('religion', 'opening_hours',
                       'internet_access', 'building',
                       'denomination'),
        }),
    )
    readonly_fields = ('created_on', 'updated_on',
                       'osm_id', 'latitude',
                       'longitude', 'country',
                       'city', 'postcode',
                       'street', 'phone',
                       'email', 'religion',
                       'opening_hours', 'internet_access',
                       'opening_hours', 'internet_access',
                       'building', 'denomination')


@django.contrib.admin.register(models.GeoName)
class GeoNameAdmin(django.contrib.admin.ModelAdmin):
    list_display = ('geoname_id', 'osm_id',
                    'latitude', 'longitude',
                    'name', 'alt_name',
                    'country_code', 'location_map')

    search_fields = ('geoname_id', 'osm__id',
                     'latitude', 'longitude',
                     'name', 'country_code')
    ordering = ('-created_on', )
    fieldsets = (
        ('Status', {
            'fields': ('created_on', 'updated_on', 'geoname_id', ),
        }),
        ('Basic Information', {
            'fields': ('name', 'alt_name', 'osm'),
        }),
        ('Address Information', {
            'fields': ('latitude', 'longitude',
                       'location_map', 'parent_country',
                       'nearby_features'),
        }),
        ('Others', {
            'fields': ('feature_class', 'feature_code',
                       'parent_feature', 'wikipedia_article'),
        }),
    )
    readonly_fields = ('created_on',
                       'updated_on',
                       'geoname_id',)


@django.contrib.admin.register(models.School)
class SchoolAdmin(django.contrib.admin.ModelAdmin):
    list_display = ('school_id', 'osm_id',
                    'latitude', 'longitude',
                    'latitude27', 'longitude27',
                    'name', 'region',
                    'category')
    search_fields = ('school_id', 'osm__id',
                     'latitude', 'longitude',
                     'name', 'region',
                     'category', 'gender')
    ordering = ('-created_on', )
    fieldsets = (
        ('Status', {
            'fields': ('created_on', 'updated_on', 'school_id', 'osm'),
        }),
        ('School Information', {
            'fields': ('name', 'category',
                       'gender', 'directorate',
                       'code'),
        }),
        ('Geo Location Information', {
            'fields': ('latitude', 'longitude',
                       'latitude27', 'longitude27'),
        }),
        ('Address Information', {
            'fields': ('region', 'location',),
        }),
    )
    readonly_fields = ('created_on',
                       'updated_on',
                       'school_id',
                       'osm')
