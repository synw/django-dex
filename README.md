# Django Dex

Database export tools. Features:

- Clone a Django database into another Django database
- Export a Django database to an external database

## Install

Install dependencies:

   ```bash
   pip install influxdb
   ```
   
Clone and add to installed apps:

   ```python
   "dex",
   ``` 
   
## Management commands
   
### Clone a Django database into another Django database

   ```bash
   python3 manage.py clonedb default replica
   ```
   
Where `default` and `replica` are registered databases in settings.DATABASES

Option:

`-apps`: apps to export: ex: python3 manage.py clonedb default replica -apps=auth,myapp1,myapp2

`-m`: to migrate the destination database before copying data

   
### Export a Django database to an external database

#### Supported databases

- Influxdb

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

   ```bash
   python3 manage.py dexport timeseries
   ```
   
This will export all the models to the timeseries database declared in settings

Options:

`-a appname`: export only this app

`-t fieldname`: name of the field considered as timefield

`-m measurement_name`: name of the measurement in Influxbd

`-s 1`: returns json stats about exports

`-txt 0`: disable text fields in serialization: usefull for timeseries where it is not needed

Example: export from auth:

`python3 manage.py dexport timeseries -a auth -m mysite_auth -t date_joined`

#### Extra options

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
   python3 manage.py dexport timeseries -a auth -m  user_join -t date_joined -txt 0
   # auth last logins
   python3 manage.py dexport timeseries -a auth -m user_login -t last_login -txt 0
   # allauth accounts creation
   python3 manage.py dexport timeseries -a socialaccount -m social_join -t date_joined -txt 0
   # allauth last logins
   python3 manage.py dexport timeseries -a socialaccount -m social_login -t last_login -txt 0
   ```

Results in a Grafana dashboard:

![Dex auth dashboard screenshot](https://github.com/synw/django-dex/raw/master/doc/img/screenshot.png)

## Commands for django-terminal

```bash
   pip install django-downloadview
   ```
   
Add `"django_downloadview",` to installed apps.

These are command that run into [Django Terminal](https://github.com/synw/django-terminal)

[replicatedb](https://github.com/synw/django-terminal#commands): to replicate the 'default' database to the 'replica' 
sqlite database. Settings:

   ```python
   DATABASES = {
      'default': {
         # ...
       },
       'replica': {
          'ENGINE': 'django.db.backends.sqlite3',
          'NAME': os.path.join(BASE_DIR, 'replica.sqlite3'),
       }
   }
   ```
   
This command is used to clone the default db into a sqlite replica and download it.

## Todo

- [ ] Support for Rethinkdb
- [ ] Export only one model
- [ ] Register models to auto export on save
- [ ] Model level database routing
