from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(
    name='ckanext-ottawa',
    version=version,
    description="City of Ottawa Open Data Portal",
    long_description='''
    ''',
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='boxkite',
    author_email='contact@boxkite.ca',
    url='data.ottawa.ca',
    license='',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['ckanext', 'ckanext.ottawa'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    entry_points='''
        [ckan.plugins]
        # Add plugins here, e.g.
        ottawa_theme=ckanext.ottawa.plugin:OttawaThemePlugin
        ottawa_group=ckanext.ottawa.plugin:OttawaGroupPlugin
    ''',
)
