FROM python:3

WORKDIR /usr/src/app

RUN pip install mysql-connector logger pyyaml

CMD [ "python" ]