ckan.plugins = ... fluent scheming ottawa_theme wet_theme


Migrations from CKAN 1.8
------------------------

Change `ckan.plugins` to:
```fluent ottawa_theme ottawa_forms wet_theme```

Then run the `migrate.py` script

Afterwards, change `ckan.plugins` back to the default
