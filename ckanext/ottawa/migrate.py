
# coding: utf-8

# In[1]:

import ckanapi
import markdown
import time


# In[2]:

ckan = ckanapi.RemoteCKAN("http://data.ottawa.ca/")
ckan_v2 = ckanapi.RemoteCKAN("http://boot2docker:5698/", apikey="baebeea6-b6b8-4a5d-95f9-986ab15dfdb4")


# In[3]:

#move groups to organizations
groups = ckan.action.group_list()

for name in groups:
    group = ckan.action.group_show(id=name)
    group_v2 = ckan_v2.action.organization_create(name=group['name'],
                                                  id=group['id'],
                                                  title=group['title'],
                                                  description=group['description'],
                                                  image_url=group['image_url'],
                                                  state=group['state'],
                                                  approval_status=group['approval_status'],
                                                  )
    print "Created Organization {0}".format(group_v2['name'])


# In[4]:

#create new groups
new_groups = {'city-hall': 'City Hall', 
              'business-and-economy': 'Business & Economy', 
              'demographics': 'Demographics', 
              'environment': 'Environment', 
              'geography-and-maps': 'Geography and Maps', 
              'living': 'Living', 
              'health-and-safety': 'Health and Safety', 
              'planning-and-development': 'Planning & Development', 
              'transportation': 'Transportation'}

for g in new_groups:
    group_dict = {'name': g, 'title': new_groups[g]}
    ckan_v2.action.group_create(**group_dict)


# In[5]:

def import_packages(package_list):
    for name in package_list:
        package = ckan.action.package_show(id=name)
        #groups = [{'name': group['name']} for group in package['groups']]

        group = ''
        if package.get('groups', None):
            group = package['groups'][0]['name']

        v2 = {
            'id': package['id'],
            'owner_org': group,
            'maintainer': package['maintainer'],
            'maintainer_email': package['maintainer_email'],
            'frequency': {'en': package['update_frequency'].replace('"', ''), 
                          'fr': package['frequence_a_jour'].replace('"', '').decode('unicode-escape')},
            'author': package['author'],
            'author_email': package['author_email'],
            'description': {'en': markdown.markdown(package['notes'].replace('"', '').replace("\\r", '').replace("\\n", '\n')), 
                            'fr': markdown.markdown(package['resume'].replace('"', '').decode('unicode-escape'))},
            'resources': package['resources'],
            'accuracy': {'en': markdown.markdown(package['accuracy'].replace('"', '').replace("\\r", '').replace("\\n", '\n')), 
                         'fr': markdown.markdown(package['exactitude'].replace('"', '').decode('unicode-escape'))},
            'date_published': package['date_published'].replace('"', ''),
            'title': {'en': package['title'].replace('"', ''), 
                      'fr': package['titre'].replace('"', '').decode('unicode-escape')},
            'name': package['name'],
            'attributes': {'en': markdown.markdown(package['attributes'].replace('"', '').replace("\\r", '').replace("\\n", '\n')), 
                           'fr': markdown.markdown(package['supplementaires'].replace('"', '').decode('unicode-escape'))}
        }

        try:
            package_v2 = ckan_v2.action.package_create(id=v2['id'],
                                               name=v2['name'],
                                               owner_org=v2['owner_org'],
                                               maintainer=v2['maintainer'],
                                               maintainer_email=v2['maintainer_email'],
                                               frequency=v2['frequency'],
                                               author=v2['author'],
                                               author_email=v2['author_email'],
                                               description=v2['description'],
                                               resources=v2['resources'],
                                               accuracy=v2['accuracy'],
                                               data_published=v2['date_published'],
                                               title=v2['title'],
                                               attributes=v2['attributes'],
                                               type='dataset')
        except ckanapi.CKANAPIError:
            print "could not create package {0}".format(v2['name'])
            continue

        print "Created Package {0}".format(package_v2['name'])


# In[6]:

packages = ckan.action.package_list()
for package in packages:
    import_packages([package])
    #uncomment next line if you want to stagger imports for fear of overloading datapusher
    #import time; time.sleep(5)


# In[ ]:

#files datastore has problems with:
#http://data.ottawa.ca/storage/f/2014-09-29T190031/City-of-Ottawa-Drinking-Water-Data-Summary.zip
#http://data.ottawa.ca/en/storage/f/2013-07-25T200519/2013-Q1-Operating-Status-Report.xlsx
#http://data.ottawa.ca/en/storage/f/2013-09-17T135414/Open-Data-Q2-2013.xlsx
#http://join.ottawa.ca/open_data/feeds/scheds - interesting one


# In[67]:

for p in ckan_v2.action.package_list():
    package = ckan_v2.action.package_show(id=p)
    package['license_id'] = 'ottawa'
    ckan_v2.action.package_update(**package)


# In[ ]:

#migrate files
packages = ckan_v2.action.package_list()
for p in packages:
    package = ckan_v2.action.package_show(id=p)
    for resource in package['resources']:
        if resource['resource_type'] in ['file.upload', 'file', None]:
            f = requests.get(resource['url'], stream=True)
            name = resource['url'].split('/')[-1]
            resource['upload'] = (name, f.raw)
            ckan_v2.action.resource_update(**resource)
            f.close()
        else:
            print "skipping resource {0}, type is: {1}".format(resource['name'].encode('utf-8'), resource['resource_type'])

