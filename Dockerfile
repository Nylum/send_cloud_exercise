FROM python:3.8.6

WORKDIR /
COPY ["requirements.txt", "application.py", "config.py", "db_initializer.py", "docker/app.sh", "fabfile.py", "./"]
COPY ["manager", "./manager"]

RUN pip3 install --no-cache-dir -r requirements.txt
RUN rm requirements.txt

ENTRYPOINT ["./app.sh"]