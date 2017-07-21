# Django Dex

Database export tools.

## Supported database

- Influxdb

## Install

Clone and add `"dex",` to installed apps. Install dependencies:

   ```bash
   pip install influxdb
   ```

Configure your databases in settings:

   ```python
   DEX_DBS = {
    "timeseries": {
        "type": "influxdb",
        "db": "database_name",
        "host": "localhost",
        "port": 8086,
        "user": "admin",
        "password": "admin"
    },
   }
   ```
   
## Usage

   ```bash
   python3 manage.py dexport timeseries
   ```
   
This will export all the models to the timeseries database declared in settings

Options:

`-a appname`: export only this app

`-t fieldname`: name of the field considered as timefield

`-m measurement_name`: name of the measurement in Influxbd

`-s 1`: returns json stats about exports

Example: export from auth:

`python3 manage.py dexport timeseries -a auth -m mysite_auth -t date_joined`

## Extra options

Set different time fields for models:

   ```python
   DEX_TIME_FIELDS = {
    "User": "date_joined",
    "SocialAccount": "date_joined"
   }
   ```
 
 Set different serializers for models:
 
   ```python
   DEX_SERIALIZERS = {
    "MyModel": ("myapp.serializer", ["field1", "field2"]),
   }
   ```
   
The key is the model name, first parameter in tuple is the serializer path and the second is the fields to be prefectched when
querying for model instances.

## Example

Export auth and socialaccount (from django-allauth) using an Influxdb database:

   ```bash
   # auth account creation
   python3 manage.py dexport timeseries -a auth -m  user_join -t date_joined
   # auth last logins
   python3 manage.py dexport timeseries -a auth -m user_login -t last_login
   # allauth accounts creation
   python3 manage.py dexport timeseries -a socialaccount -m social_join -t date_joined
   # allauth last logins
   python3 manage.py dexport timeseries -a socialaccount -m social_login -t last_login
   ```

Results in a Grafana dashboard:

![Dex auth dashboard screenshot](https://github.com/synw/django-dex/raw/master/doc/img/screenshot.png)

## Todo

- [ ] Support for Rethinkdb
- [ ] Export only one model
- [ ] Register models to auto export on save
- [ ] Model level database routing
