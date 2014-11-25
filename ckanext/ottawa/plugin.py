import ckan.plugins as p

from ckan.plugins.interfaces import IDatasetForm
from ckan.lib.plugins import DefaultDatasetForm
from ckan.logic.schema import default_create_package_schema
from ckan.lib.navl.validators import ignore_missing
from ckan.new_authz import is_sysadmin
from ckan.logic.validators import name_validator
from ckanext.scheming.plugins import SchemingDatasetsPlugin

class OttawaThemePlugin(p.SingletonPlugin):
    p.implements(p.IConfigurable, inherit=True)
    p.implements(p.IRoutes, inherit=True)
    p.implements(p.IConfigurer, inherit=True)

    def configure(self, config):
        pass

    def update_config(self, config):
        p.toolkit.add_template_directory(config, 'templates')
        p.toolkit.add_public_directory(config, 'public')


class OttawaFormsPlugin(SchemingDatasetsPlugin):
    """
    This plugin uses scheming_datasets, which is why we don not add
    scheming_datasets to ckan.plugins.

    The main purpose of overriding this is for migration - we want to keep
    the old CKAN 1.8 portal ids in 2.2. May remove this code later when no
    longer needed.
    """
    p.implements(IDatasetForm, inherit=True)

    def is_fallback(self):
        return True

    def package_types(self):
        return []

    def create_package_schema(self):
        schema = default_create_package_schema()
        _schema_update(schema)

        return schema


def _schema_update(schema):
    schema['id'] = [ignore_missing, protect_new_dataset_id,
            unicode, name_validator, package_id_doesnt_exist]


def protect_new_dataset_id(key, data, errors, context):
    """
    Allow dataset ids to be set for packages created by a sysadmin
    """
    if is_sysadmin(context['user']):
        return
    empty(key, data, errors, context)


def package_id_doesnt_exist(key, data, errors, context):
    """
    fail if this value already exists as a package id.
    """

    model = context["model"]
    session = context["session"]
    existing = model.Package.get(data[key])
    if existing:
        errors[key].append(_('That URL is already in use.'))
