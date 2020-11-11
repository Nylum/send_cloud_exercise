from invoke import run
from fabric import task


@task
def launcher(context):
    run("flask run --host=127.0.0.1 --port=5000")


@task
def initdb(context):
    run("python db_initializer.py init_db")


@task
def migratedb(context):
    run("python db_initializer.py db migrate")
    run("python db_initializer.py db upgrade")
