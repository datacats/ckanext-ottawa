
# In[1]:

import ckanapi
import markdown


# In[2]:

ckan = ckanapi.RemoteCKAN("http://data.ottawa.ca/")
ckan_v2 = ckanapi.RemoteCKAN("http://boot2docker:5698/", apikey="3067dd7b-945f-44f4-a090-3c990a4ccd83")


# In[15]:

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


# In[16]:

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


# In[18]:

packages = ckan.action.package_list()
import_packages(packages)


# In[4]:

for p in ckan_v2.action.package_list():
    package = ckan_v2.action.package_show(id=p)
    package['license_id'] = 'ottawa'
    ckan_v2.action.package_update(**package)


# In[ ]:



