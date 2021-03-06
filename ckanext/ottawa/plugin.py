import ckan.plugins as p
import ckan.lib.helpers as h
import json
import logging
import ckanapi
import ckan.model as model

from ckan.plugins.interfaces import IDatasetForm
from ckan.lib.plugins import DefaultDatasetForm, DefaultGroupForm, DefaultOrganizationForm
from ckan.logic.schema import default_create_package_schema, group_form_schema
from ckan.logic import get_action
from ckan.lib.navl.validators import ignore_missing
from ckan.new_authz import is_sysadmin
from ckan.logic.validators import name_validator
from ckan.logic.converters import convert_to_extras, convert_from_extras
from ckan.lib.navl.validators import ignore_missing, not_empty
from ckanext.scheming.plugins import SchemingDatasetsPlugin

log = logging.getLogger(__name__)

class OttawaGroupPlugin(p.SingletonPlugin, DefaultGroupForm):
    p.implements(p.IGroupForm, inherit=True)

    def is_fallback(self):
        return True

    def group_types(self):
        return ['group']

    def group_form(self):
        return 'group/ottawa_form.html'

    def form_to_db_schema(self):
        schema =  group_form_schema()
        schema.update({
            'title_fr': [ignore_missing, unicode, convert_to_extras],
            'description_fr': [ignore_missing, unicode, convert_to_extras],
        })

        return schema

    def db_to_form_schema(self):
        schema = group_form_schema()
        schema.update({
            'title_fr': [convert_from_extras, ignore_missing],
            'description_fr': [convert_from_extras, ignore_missing],
        })

        return schema

    def setup_template_variables(self, context, data_dict):
        pass

class OttawaOrgPlugin(p.SingletonPlugin, DefaultOrganizationForm):
    p.implements(p.IGroupForm, inherit=True)

    def is_fallback(self):
        return False

    def group_types(self):
        return ['organization']

    def group_form(self):
        return 'group/ottawa_form.html'

    def form_to_db_schema(self):
        schema =  group_form_schema()
        schema.update({
            'title_fr': [ignore_missing, unicode, convert_to_extras],
            'description_fr': [ignore_missing, unicode, convert_to_extras]
        })

        return schema

    def db_to_form_schema(self):
        schema = group_form_schema()
        schema.update({
            'title_fr': [convert_from_extras, ignore_missing],
            'description_fr': [convert_from_extras, ignore_missing]
        })

        return schema

    def setup_template_variables(self, context, data_dict):
        pass

class OttawaThemePlugin(p.SingletonPlugin):
    p.implements(p.IConfigurable, inherit=True)
    p.implements(p.IRoutes, inherit=True)
    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.ITemplateHelpers, inherit=True)

    def configure(self, config):
        pass

    def update_config(self, config):
        p.toolkit.add_template_directory(config, 'templates')
        p.toolkit.add_public_directory(config, 'public')
        p.toolkit.add_resource('fanstatic', 'ottawa')

        h.dataset_display_name = _dataset_display_name

    def get_helpers(self):
        return {
            'resource_tags': _filter_resource_tags,
            'groups': _home_groups,
            'title': _title_from_solr,
            'french_group_name': _french_group_name
        }

def _title_from_solr(title_str, lang):
    return json.loads(title_str)[lang]

def _home_groups():
    gps = []
    ckan = ckanapi.LocalCKAN()
    groups = ckan.action.group_list()
    for g in groups:
        gps.append(ckan.action.group_show(id=g))

    return gps

def _filter_resource_tags(package):
    """
    Returns resource links for a package such that any resource with a unique
    format returns a link to the resource, and any link with a duplicate format
    returns a link to the package page.
    """
    res_list = []
    all_res = h.dict_list_reduce(package['resources'], 'format', unique=False)
    uniques = [x for x in all_res if all_res.count(x) == 1]
    non_uniques = set(all_res) - set(uniques)

    for resource in package['resources']:
        if resource['format'] in uniques:
            res_list.append({
                'format': resource['format'],
                'url': h.url_for(controller='package',
                                 action='resource_read',
                                 id=package['name'],
                                 resource_id=resource['id'])
            })
        elif resource['format'] in non_uniques:
            res_list.append({
                'format': resource['format'],
                'url': h.url_for(controller='package',
                                 action='read',
                                 id=package['name'])
            })
            non_uniques.remove(resource['format'])

    return res_list

def _dataset_display_name(package_or_package_dict):
    if type(package_or_package_dict) is dict:
        title = package_or_package_dict['title']
    else:
        title = package_or_package_dict.title

    if isinstance(title, dict):
        display = title[h.lang()]
    else:
        display = json.loads(title)[h.lang()]
    return display

def db_to_form_schema(group_type='group'):
    from ckan.lib.plugins import lookup_group_plugin
    return lookup_group_plugin(group_type).db_to_form_schema()

def _french_group_name(group_dict, org=False):
    """
    CKAN doesn't give us the full group dict on /groups, but we need it
    """
    action = 'organization_show' if org else 'group_show'
    context = {'model': model, 'session': model.Session,
               'ignore_auth': True,
               'schema': db_to_form_schema(),
               'for_view': True}
    data_dict = {'id': group_dict['id'], 'include_datasets': True}

    group = get_action(action)({}, {'id': group_dict['name']})

    return group.get('title_fr', group['display_name'])
