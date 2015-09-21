"""Import GIS dataset resources into CKAN

Usage:
    geoimport (-g GIS_REPO) (-m MAPPING) (-r CKAN_URL) (-a APIKEY)

Options:
    -g --gis        Location of the GIS resource repo to import from
    -m --mapping    Location of the YAML file where resource mappings are stored
    -r --remote     CKAN URL
    -a --apikey     CKAN API Key to use when importing
"""

import os
import yaml
import ckanapi
import zipfile
import requests

from docopt import docopt
from datetime import datetime
from dateutil.parser import parse

arguments = docopt(__doc__)

stream = open(arguments['MAPPING'], 'r')
mapping =  yaml.load(stream)

ckan = ckanapi.RemoteCKAN(arguments['CKAN_URL'], apikey=arguments['APIKEY'])
base_import_url = arguments['GIS_REPO']

def download_temp_file(resource_path, file_name):
        r = requests.get(resource_path, stream=True)
        if r.status_code == 200:
            if r.headers['content-type'] == 'text/xml':
                with open(file_name, 'w') as f:
                    f.write(r.content)
                    f.close()
                return True
            else:
                with open(file_name, 'wb') as f:
                    for chunk in r.iter_content():
                        f.write(chunk)
                    f.close()
                return True
        else:
            return False

def upload_file_to_resource(resource, file_object):
    filename = "{0}.{1}".format(resource['name'], resource['format'])
    if resource['format'].lower() == 'shp':
        filename = "{0}.{1}.zip".format(resource['name'], resource['format'])
    resource['upload'] = (filename, file_object)
    resource['last_modified'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
    ckan.action.resource_update(**resource)

def import_shapefile(resource, mapping):
    shape_destination_dir = os.path.join('temp_data', resource['name'] + '_shp')
    if not os.path.exists(shape_destination_dir):
        os.makedirs(shape_destination_dir)

    for shape_format, shape_location in mapping['shp'].iteritems():
        resource_location = base_import_url + shape_location
        file_name = "{0}.{1}".format(resource['name'], shape_format)
        download_location = os.path.join(shape_destination_dir, file_name)
        download_temp_file(resource_location, download_location)

    zip_filename = os.path.join('temp_data', resource['name'] + '.shp.zip')
    zip = zipfile.ZipFile(zip_filename, 'w')
    for root, dirs, files in os.walk(shape_destination_dir):
        for file in files:
            zip.write(os.path.join(root, file), file)
    zip.close()


    upload_file_to_resource(resource, open(zip_filename))


def get_import_url(resource, mapping):
    afile = mapping[resource['format'].lower()]

    if resource['format'].lower() == 'shp':
        afile = mapping[resource['format'].lower()]['shp']

    import_file = "{0}{1}".format(base_import_url, afile)

    return import_file

def get_import_file_date(import_file):
    head = requests.head(import_file)
    date_modified = parse(head.headers['last-modified']).replace(tzinfo=None)

    return date_modified

def out_of_date(resource, import_file):
    date_modified = get_import_file_date(import_file)
    resource_modified = parse(resource['last_modified']).replace(tzinfo=None)

    if date_modified > resource_modified:
        return True
    else:
        return False

def perform_import(resource, mapping):
    print "updating resource {0}:{1}".format(resource['name'], resource['format'])

    if resource['format'].lower() == 'shp':
        import_shapefile(resource, mapping)
    else:
        url = get_import_url(resource, mapping)
        f = requests.get(url, stream=True)
        upload_file_to_resource(resource, f.raw)
        f.close()

for dataset, resources_mapping in mapping.iteritems():
    try:
        package = ckan.action.package_show(id=dataset)
    except ckanapi.errors.NotFound:
        print "dataset not found: {0}".format(dataset)
        continue

    existing_formats = [res['format'].lower() for res in package['resources']]
    for resource_format in resources_mapping:
        if resource_format not in existing_formats:
            resource = create_resource(package, resource_format)
        else:
            resource = [res for res
                in package['resources']
                if res['format'] == resource_format
                ][0]

        import_file = get_import_url(res, resources_mapping)
        if out_of_date(res, import_file):
            perform_import(res, resources_mapping)
