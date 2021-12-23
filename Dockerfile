FROM python:3.9

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir pytest


COPY . .

CMD [ "pytest", "--junitxml=/usr/src/report junitxml" ]