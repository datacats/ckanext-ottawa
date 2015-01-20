```
ckan.plugins = ... resource_proxy geojson_preview webhooks ottawa_theme pages fluent scheming_datasets scheming_groups scheming_organizations wet_theme

ckanext.webhooks.eventloop = http://192.168.1.107:8765
ckan.datapusher.url      = http://192.168.1.107:8800

wet_theme.url = http://boot2docker:5698/theme-base
wet_theme.geo_map_type = static

scheming.dataset_schemas = ckanext.ottawa:dataset_schema.json
scheming.group_schemas = ckanext.ottawa:group_schema.json
scheming.organization_schemas = ckanext.ottawa:org_schema.json

ckanext.pages.wysiwyg = True

ckan.max_resource_size = 100

ckan.site_url = http://must_be_set_to_proper_site_url.com

licenses_group_url = http://path.to.ottawa.license

ckan.locales_offered=en fr
```

Migrations from CKAN 1.8
------------------------

Run the `migrate.py` script
