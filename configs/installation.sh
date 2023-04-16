#!/bin/bash

sudo apt update
sudo apt-get install libsndfile1
sudo apt install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools python3-venv nginx

# Make python env and clone project

python3 -m venv {env_name}
source {env_name}/bin/activate
pip install wheel
pip install -U pip

git clone {repo_link}
pip install -r {repo_name}/requirements.txt 


# Gunicorn conf

sudo cp videofy/config/gunicorn.service /etc/systemd/system/
cd /var/log/
sudo mkdir gunicorn
cd gunicorn/
sudo touch access.log
sudo touch error.log

cd
sudo chmod 777 /var/log/gunicorn/access.log
sudo chmod 777 /var/log/gunicorn/error.log

sudo systemctl enable gunicorn
sudo systemctl start gunicorn
sudo systemctl restart gunicorn
sudo systemctl status gunicorn


# Nginx conf

sudo cp {repo_name}/config/nginx /etc/nginx/sites-available/{nginx_file_name}
sudo ln -s /etc/nginx/sites-available/{nginx_file_name} /etc/nginx/sites-enabled

sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/{key_name}.key -out /etc/ssl/certs/{crt_name}.crt

sudo nginx -t
sudo systemctl restart nginx
sudo ufw delete allow 5000
sudo ufw allow 'Nginx Full'

sudo systemctl status nginx


# Celery conf

sudo apt-get install curl gnupg apt-transport-https -y

## Team RabbitMQ's main signing key
curl -1sLf "https://keys.openpgp.org/vks/v1/by-fingerprint/0A9AF2115F4687BD29803A206B73A36E6026DFCA" | sudo gpg --dearmor | sudo tee /usr/share/keyrings/com.rabbitmq.team.gpg > /dev/null
## Cloudsmith: modern Erlang repository
curl -1sLf https://dl.cloudsmith.io/public/rabbitmq/rabbitmq-erlang/gpg.E495BB49CC4BBE5B.key | sudo gpg --dearmor | sudo tee /usr/share/keyrings/io.cloudsmith.rabbitmq.E495BB49CC4BBE5B.gpg > /dev/null
## Cloudsmith: RabbitMQ repository
curl -1sLf https://dl.cloudsmith.io/public/rabbitmq/rabbitmq-server/gpg.9F4587F226208342.key | sudo gpg --dearmor | sudo tee /usr/share/keyrings/io.cloudsmith.rabbitmq.9F4587F226208342.gpg > /dev/null

## Add apt repositories maintained by Team RabbitMQ
sudo tee /etc/apt/sources.list.d/rabbitmq.list <<EOF
## Provides modern Erlang/OTP releases
##
deb [signed-by=/usr/share/keyrings/io.cloudsmith.rabbitmq.E495BB49CC4BBE5B.gpg] https://dl.cloudsmith.io/public/rabbitmq/rabbitmq-erlang/deb/ubuntu bionic main
deb-src [signed-by=/usr/share/keyrings/io.cloudsmith.rabbitmq.E495BB49CC4BBE5B.gpg] https://dl.cloudsmith.io/public/rabbitmq/rabbitmq-erlang/deb/ubuntu bionic main

## Provides RabbitMQ
##
deb [signed-by=/usr/share/keyrings/io.cloudsmith.rabbitmq.9F4587F226208342.gpg] https://dl.cloudsmith.io/public/rabbitmq/rabbitmq-server/deb/ubuntu bionic main
deb-src [signed-by=/usr/share/keyrings/io.cloudsmith.rabbitmq.9F4587F226208342.gpg] https://dl.cloudsmith.io/public/rabbitmq/rabbitmq-server/deb/ubuntu bionic main
EOF

## Update package indices
sudo apt-get update -y

## Install rabbitmq-server and its dependencies
sudo apt-get install rabbitmq-server -y --fix-missing

sudo systemctl status rabbitmq-server.service

sudo systemctl restart rabbitmq-server.service

sudo apt-get install supervisor

cd /var/log/
sudo mkdir celery
cd

sudo touch /var/log/celery/celery_stdout.log
sudo touch /var/log/celery/celery_stderr.log

sudo chmod 777 /var/log/celery/celery_stdout.log
sudo chmod 777 /var/log/celery/celery_stderr.log

sudo cp videofy/config/celery.conf /etc/supervisor/conf.d/

sudo supervisorctl reload all
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart all



# sudo journalctl -u gunicorn -n 100 -f

# sudo nano /etc/nginx/nginx.conf

# client_max_body_size 2G;

# sudo systemctl daemon-reload
# sudo systemctl restart gunicorn
# sudo systemctl restart nginx

# sudo systemctl status gunicorn
# sudo systemctl status nginx
