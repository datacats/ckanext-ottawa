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
