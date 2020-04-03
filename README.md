
# Ecommerce
### Documentation:

1. [Django](https://docs.djangoproject.com/en/2.0/releases/2.0/)
2. [Markdown](https://bitbucket.org/tutorials/markdowndemo), used for the formatting of this README file.
3. [Django JET](http://jet.readthedocs.io/en/latest/)

### Installation:

##### -> you must install Elastic Search on your computer (you can use brew)

##### System Dependencies:

1. Install git on Linux:  
`sudo apt-get install -y git`
2. Clone or download this repo.
3. Install pip and vitualenv on Linux:  
`sudo apt-get install -y virtualenv`  
`sudo apt-get install -y python3-pip`
4. Create a virtual environment on Linux or Mac:  
`virtualenv -p python3 ~/.virtualenvs/ecommerce`
5. Activate the virtual environment on Linux or Mac:  
`source ~/.virtualenvs/ecommerce/bin/ecommerce`
6. Install requirements in the virtualenv:  
`pip3 install -r requirements.txt`

##### Relational database dependencies (PostgreSQL):
1. Install components for Ubuntu:  
`sudo apt-get update`  
`sudo apt-get install python-dev libpq-dev postgresql postgresql-contrib`
2. Switch to **postgres** (PostgreSQL administrative user):  
`sudo su postgres`
3. Log into a Postgres session:  
`psql`
4. Create database with name **ecommerce**:  
`CREATE DATABASE ecommerce;`
5. Create a database user which we will use to connect to the database:  
`CREATE USER ecommerce_user WITH PASSWORD 'ecommerce_pass';`
6. Modify a few of the connection parameters for the user we just created:  
`ALTER ROLE ecommerce_user SET client_encoding TO 'utf8';`  
`ALTER ROLE ecommerce_user SET default_transaction_isolation TO 'read committed';`  
`ALTER ROLE ecommerce_user SET timezone TO 'UTC';` 
7. Give our database user access rights to the database we created:  
`GRANT ALL PRIVILEGES ON DATABASE ecommerce TO ecommerce_user;`
8. Exit the SQL prompt and the postgres user's shell session:  
`\q` then `exit`

9. Activate the virtual environment:  
`source ~/.virtualenvs/ecommerce/bin/activate`
10. Make Django database migrations:
`python manage.py makemigrations`  
then: `python manage.py migrate`

##### Use admin interface:
1. Create an admin user:  
`python manage.py dosuperuser`
2. Run the project locally:  
`python manage.py runserver`
3. Navigate to: `http://localhost:8000/admin/`
 
##### Steps for install Celery and work it.
1. pip install -r requirements.txt
2. sudo apt-get install -y erlang
3. sudo apt-get install rabbitmq-server
4. sudo systemctl enable rabbitmq-server
5. sudo systemctl start rabbitmq-server to check if rabbitmq is working run: systemctl status rabbitmq-server
6. run local server for backend
7. run this command in new terminal in project path with activating virtual env: celery -A ecommerce worker -l info


## Setup for Django Channels 
1. [Django Channels Deploy](https://channels.readthedocs.io/en/latest/deploying.html)
2. [Daphne](https://github.com/django/daphne)
3. [Django Channels configration on server](https://github.com/django/channels/issues/972)

#### - if you face any problems on server pleas run these commands on production
1. sudo service supervisor stop
2. sudo service supervisor start
3. sudo supervisorctl reread
4. sudo supervisorctl update
5. sudo service nginx restart
6. sudo service apache2 restart


### API Endpoints
##### Register
Method: `POST`  
Endpoint: `/registration/`  
Payload:  
`{  
    "username": "USERNAME",  
    "password1": "PASSWORD",  
    "password2": "PASSWORD",  
    "email": "OPTIONAL_EMAIL"  
}`
##### Login
Method: `POST`  
Endpoint: `/login/`  
Payload:  
`{  
    "username": "USERNAME",  
    "password": "PASSWORD"  
}`

##### Logout
Method: `POST`  
Endpoint: `/logout/`  
Headers: `Authorization: JWT YOUR_TOKEN_HERE`  


### Admin Credentials
### Username: `admin`  
### Password: `admin` 

## For Dump and Load data

##### you should creating a folder to do this operations

##### for dump data from database:

###### python manage.py dumpdata products --format json --indent 4 > products/fixures/products.json

##### For loading data into database:
###### python manage.py loaddata products/fixures/products.json

## dump and restoredatabase:
#### pg_dump dbname=ecommerce -f /tmp/ecommerce.psql
#### pg_restore -v --host=<host> --port=5432 --username=<username> --password --dbname=ecommerce /tmp/ecommerce.psql


###### Note:
###### https://upload.pypi.org/legacy/