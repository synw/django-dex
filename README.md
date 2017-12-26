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
   
## Management commands
   
### Clone a Django database into another Django database

   ```bash
   python3 manage.py clonedb default replica
   ```
   
Where `default` and `replica` are registered databases in settings.DATABASES:

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

Option:

`-apps`: apps to export:

   ```
   python3 manage.py clonedb default replica -apps=auth,myapp1,myapp2
   ```

`-m`: to migrate the destination database before copying data

`verb`: verbosity level. To mute it:

   ```
   python3 manage.py clonedb default replica -verb 0
   ```


### Commands for django-terminal

```bash
   pip install django-downloadview
   ```
   
Add `"django_downloadview",` to installed apps.

Add `url('^dex/', include('dex.urls')),` to urls.

These are command that run into [Django Terminal](https://github.com/synw/django-terminal)

[replicatedb](https://github.com/synw/django-terminal#commands): to replicate 
the 'default' database to the 'replica' sqlite database.
   
This command is used to clone the default db into a sqlite replica and download it.

## Todo

- [ ] Humanize time duration
- [ ] Better looking output
- [ ] Export only one model
- [ ] Register models to auto export on save
- [ ] Model level database routing
