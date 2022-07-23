FROM python:3.8
LABEL author="Pete Tran"

WORKDIR /app
COPY ./project/techtrends/requirements.txt /app

RUN pip3 install -r requirements.txt
EXPOSE 3111
COPY ./project/techtrends/ /app
RUN python3 /app/init_db.py

CMD ["python3", "/app/app.py"]