
# In[90]:

import ckanapi


# In[127]:

ckan = ckanapi.RemoteCKAN("http://data.ottawa.ca/", apikey="...")
ckan_v2 = ckanapi.RemoteCKAN("http://localhost/", apikey="...")


# In[128]:

packages = ckan.action.package_list()


# In[129]:

for name in packages:
    package = ckan.action.package_show(id=name)
    v2 = {
        'maintainer': package['maintainer'],
        'maintainer_email': package['maintainer_email'],
        'frequency': {'en': package['update_frequency'].replace('"', ''), 'fr': package['frequence_a_jour'].replace('"', '').decode('unicode-escape')},
        'author': package['author'],
        'author_email': package['author_email'],
        'description': {'en': package['notes'].replace('"', ''), 'fr': package['resume'].replace('"', '').decode('unicode-escape')},
        'resources': package['resources'],
        'accuracy': {'en': package['accuracy'].replace('"', ''), 'fr': package['exactitude'].replace('"', '').decode('unicode-escape')},
        'date_published': package['date_published'].replace('"', ''),
        'title': {'en': package['title'], 'fr': package['titre'].replace('"', '').decode('unicode-escape')},
        'name': package['name'],
        'attributes': {'en': package['attributes'].replace('"', ''), 'fr': package['supplementaires'].replace('"', '').decode('unicode-escape')}
    }

    package_v2 = ckan_v2.action.package_create(name=v2['name'],
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


# In[ ]:
