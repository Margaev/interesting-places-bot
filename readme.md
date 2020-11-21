### Telegram bot that can suggest you where to go.

#### Installation:
1) Create venv 

    `$ python3 -m venv venv`
2) Install requirements 

    `$ pip install -r requirements.txt`
3) Create interesting_places_bot/local_settings.py file and fill it by example:
    ```
    ALLOWED_HOSTS = ['127.0.0.1', 'your_host']
    SECRET_KEY = 'secret_key'
    
    TELEGRAM_BOT_TOKEN = 'your_token'
    URL = 'your_host'
    
    DATABASES = {
        'default': {
            'ENGINE': 'django.contrib.gis.db.backends.postgis',
            'NAME': 'db_name',
            'USER': 'username',
            'PASSWORD': 'password',
            'HOST': 'db_host',
            'PORT': 'db_port',
        }
    }
    ```
4) Create migrations:

    ```
   $ python3 manage.py makemigrations
   $ python3 manage.py migrate
   ```
5) Run server:

    `$ python3 manage.py runserver`