### Telegram bot that can suggest you where to go.

#### Installation:
1) Create venv 

    `$ python3 -m venv venv`
2) Install requirements 

    `$ pip install -r requirements.txt`
3) Create interesting_places_bot/local_settings.py file and fill it by example:
    ```
    URL = 'your_host'
    ALLOWED_HOSTS = ['127.0.0.1', URL]
    SECRET_KEY = 'secret_key'
    
    TELEGRAM_BOT_TOKEN = 'your_token'
    
    DATABASES = {
        'default': {
            'ENGINE': 'django.contrib.gis.db.backends.postgis',
            'NAME': 'interesting_places',
            'USER': 'postgres',
            'PASSWORD': 'postgres',
            'HOST': '127.0.0.1',
            'PORT': '5000',
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