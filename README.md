# How to get up and running

## Get the environment ready
```
python3 -m venv venv 
source venv/bin/activate
```

## Migrate models
```
python3 manage.py migrate
```

## Run tests
```
python3 manage.py test
```

## Run the server
```
python3 manage.py runserver
celery -A topsuplementos worker --beat -l info
```


# Development

## Add app to to project

### Add the app to topsuplementos/settings.py INSTALLED_APPS
```
"myapp.apps.MyappConfig",
```

### Run the command
```
python3 manage.py makemigrations myapp
```


# Get the server ready for production

## Get some web server instead of the runserver command
## Serve that web server through something like apache or nginx
## Disable debug features
## AND MORE...
