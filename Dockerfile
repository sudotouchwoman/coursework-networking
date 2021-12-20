FROM python:3.8-slim

COPY ./requirements.txt /app/

COPY ./app/ /app/app/
COPY ./controller/ /app/controller/
COPY ./database/ /app/database/
COPY ./logs/ /app/logs/
COPY ./sql/ /app/sql/
COPY ./view/ /app/view/
COPY ./config/ /app/config/
COPY ./main.py /app/

WORKDIR /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 5000
ENTRYPOINT [ "python" ]
CMD [ "main.py" ]
