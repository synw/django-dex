# Django Dex

Database export tools to clone a Django database into another Django database

## Install
   
Install:

   ```bash
   pip install django-dex
   ``` 
   
Add to installed apps:

   ```bash
   "introspection",
   "dex",
   ``` 
   
## Management command

   ```bash
   python3 manage.py clonedb default replica -a -m
   ```
   
Where `default` and `replica` are registered databases in `settings.DATABASES`:

### Databases settings

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
   
### Options:

`-apps`: apps to export:

   ```
   python3 manage.py clonedb default replica -apps=auth,myapp1,myapp2
   ```

`-a`: archive the last replica

`-m`: to migrate the destination database before copying data

`-verb`: verbosity level. To mute it:

   ```
   python3 manage.py clonedb default replica -verb 0
   ```

## Commands for [django-term](https://github.com/synw/django-term)

```bash
   pip install django-downloadview
   ```
   
Add `"django_downloadview",` to installed apps.

Add `url('^dex/', include('dex.urls')),` to urls.

These are command that run into [Django Term](https://github.com/synw/django-term)

[replicatedb](https://github.com/synw/django-terminal#commands): to replicate 
the `default` database to the `replica` sqlite database.
   
This command is used to clone the default db into a sqlite replica and download it.

## Todo

- [x] Add an option to use `bulk_create` when there is no many-to-many relations
- [ ] Humanize time duration
- [ ] Export only one model
- [ ] Model level database routing
- [ ] Better looking output
- [ ] Register models to auto export on save
