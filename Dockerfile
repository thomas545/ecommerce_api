FROM python:3
ENV API_ENV 1
RUN mkdir /code
WORKDIR /Users/admin/Desktop/API_ENV/ecommerce
COPY requirements.txt /code/
RUN pip install -r requirements.txt
RUN pip install --upgrade pip
COPY . /Users/admin/Desktop/API_ENV/ecommerce/