# SendCloud Application
RSS Scraper realized for my recruitment process in SendCloud.

## Overview
The app is structured by the following:
1. Flask WebFramework
2. Celery
3. Manager
4. Swagger

### Flask WebFramework
A Flask-based API composed of several endpoints in order to support feed subscriptions and posts.
It handles the management of a user's subscribed feeds as well as looking for read/unread feed posts.
The Flask server is used only while developing, for the production phase it is using Gunicorn behind nginx reverse proxy.


### Celery
Utilizes Celery (implementation can found in `/manager/celery_periodic/worker.py`) Beat's periodic execution capabilities to periodically download feed data.
Every time the task is executed, it calls an instance of a parser, it handles as well the download, parsing and finally the storage of new feed items.
Each feed item's time of publication is checked and the Feeds's 'LastUpdated' metadata is updated in the DB, according to the most recent published FeedItem.


## State of the art (Manager)
- The DB schema (realized with SQLAlchemy and implemented in `/manager/db_model.py`) is done by the following:
`Users` can register, follow and unfollow `Feeds`, read new unread `FeedItems` and check already read `FeedItems`.
`Read` and `Unread` show which feed item was read / unread by any user.
`Follows` shows feed that the user follows.

- Feeds declaration can be found in `/config.py` , the ones provided for this exercise are [Tweakers](https://feeds.feedburner.com/tweakers/mixed) and [Algemeen](http://www.nu.nl/rss/Algemeen).

Whenever the app detects newer posts it writes them in the DB.
For each item it also creates unread relationships for each of the user that is following the feed that item was scraped from.

Users can then request new feed_items, based on the feeds they follow and choose which item to mark as read meaning the deletion of the `Unread` relationship between a specific item and a specific user and create a `Read` relationship.

## Swagger
Since that the app is lacking of a GUI the only way to consult and shoot the API collection in an easy way is the provided in `/manager/static/swagger.json` and reachable at the following address `http://localhost:1338/swagger`.


## Pre-requisites and External Dependencies
 1. Python environment - this project assumes that at least Python 3.7 is installed (I used PyCharm as IDE as well as Python itself as the project interpreter)
 2. virtualenv - make sure to copy the environment variables from `.envrc`
 3. Docker - the whole setup runs as a `docker-compose` cluster of containers
    3.1 External Container Dependencies (Already included):
    - [Postgres](https://hub.docker.com/_/postgres) (Storage)
    - [Rabbitmq](https://hub.docker.com/_/rabbitmq) (Connection between the celery workers and the broker)

## Installation
 1. Clone the repository
 2. Run `pip install -r requirements.txt` to download the project's dependencies

## How to start the application
Run `docker-compose up` and after that everything is up, shoot `fab initdb` in another terminal window from the project root in order to make the pre-population of the DB.


## Environment and configuration
Configuration is loaded from `config.py`, for the Testing and Development config everything is hardcoded.
For the sake of the exercise the production values are copied in the docker images from `docker/prod.env`
    
### Local Development Server
While everything is running, shoot `fab launcher` in another terminal window from the project root.

### Testing
With the containers running, change `FLASK_ENV` from `development` to `testing` value and shoot `pytest` in order to run the unittests coverage.

### Environment cleanup
When you're done using this app use `./scripts/cleaner.sh` to wipe all the created containers, images and volumes.
