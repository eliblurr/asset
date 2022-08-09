# E-Asset Management API service

This is a project for building an asset management system using [Fastapi](https://fastapi.tiangolo.com)  with [SQLalchemy ORM logic](https://docs.sqlalchemy.org/en/14/).

**Document contents**

- [Installation](#installation)
- [Next steps](#next-steps)
- [Contributing](#contributing)
- [Other notes](#other-notes)

# Installation

- [Docker](#setup-with-docker)
- [Virtualenv](#setup-with-virtualenv)
- [Heroku](#deploy-to-heroku)
- [AWS-EC2](#deploy-as-AWS-EC2-instance)

## Setup with Docker

#### Dependencies

- [Docker](https://docs.docker.com/engine/installation/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Installation

**Important:** This `docker-compose.yml` is configured for local testing only, and is _not_ intended for production use.

Run the following commands:

```bash
git clone https://github.com/eliblurr/asset.git
cd asset
```

Run:
```bash
mv docker.env.example docker.env
```
Setup environment variables; allowed environment variables `KEYWORDS`=`VALUES`:

| KEYWORDS | VALUES | DEFAULT VALUE | VALUE TYPE | IS REQUIRED | 
| :------------ | :---------------------: | :------------------: | :------------------: | :------------------: |
| DB_NAME | | asset | string | true |
| DB_USER | | postgres | string | true |
| DB_PASSWORD | | postgres | string | true |
| WEB_PORT | | 2000 | integer | true |
| REDIS_PORT | | 2001 | integer | true |
| PGADMIN_PORT | | 2002 | integer | true | 
| POSTGRES_PORT | | 2003 | integer | true | 
| PGADMIN_DEFAULT_EMAIL | | admin@admin.com | string | true |
| PGADMIN_DEFAULT_PASSWORD | | changeme | string | true |
| BASE_URL | | http://localhost | string | true | 
| ADMIN_EMAIL | | admin@admin.com | string | true |
| VERIFICATION_PATH | | | string | true |
| PASSWORD_RESET | | | string | true |
| EMAIL_CODE_DURATION_IN_MINUTES | | 15 | integer | true |
| ACCESS_TOKEN_DURATION_IN_MINUTES | | 60 | integer | true |
| REFRESH_TOKEN_DURATION_IN_MINUTES | | 600 | integer | true |
| PASSWORD_RESET_TOKEN_DURATION_IN_MINUTES | | 15 | integer | true |
| ACCOUNT_VERIFICATION_TOKEN_DURATION_IN_MINUTES | | 15 | integer | true |
| TWILIO_PHONE_NUMBER | | | string | false |
| TWILIO_AUTH_TOKEN | | | string | false |
| TWILIO_ACCOUNT_SID | | | string | false |
| MAIL_USERNAME | | | string | true |
| MAIL_PASSWORD | | | string | true |
| MAIL_FROM | | | string | true |
| MAIL_PORT | | | string | true |
| MAIL_SERVER | | | string | true |
| MAIL_FROM_NAME | | | string | true |
| MAIL_TLS | | true | boolean | true |
| MAIL_SSL | | false | boolean | true |
| USE_CREDENTIALS | | true | boolean | true |
| VALIDATE_CERTS | | true | boolean | true |
| DEFAULT_MAIL_SUBJECT | | | string | true |
| APS_COALESCE | | false | boolean | true |
| APS_MAX_INSTANCES | | 20 | integer | true |
| APS_MISFIRE_GRACE_TIME | | 4 | integer | true |
| APS_THREAD_POOL_MAX_WORKERS | | 20 | integer | true |
| APS_PROCESS_POOL_MAX_WORKERS | | 5 | integer | true |
| USE_S3 | | false | boolean | true |
| AWS_ACCESS_KEY_ID | | | string | true |
| AWS_SECRET_ACCESS_KEY | | | string | true |
| AWS_DEFAULT_ACL | | public-read | string | true |
| AWS_STORAGE_BUCKET_NAME | | | string | true |
| AWS_S3_OBJECT_CACHE_CONTROL | | max-age=86400 | string | true |
| REDIS_HOST | | redis | string | false |
| REDIS_PORT | | 6379 | integer | false |
| REDIS_PASSWORD | | | string | true |
| REDIS_USER | | | string | true |
| REDIS_NODE | | 0 | integer | true |
| REDIS_MAX_RETRIES | | 3 | integer | true |
| REDIS_RETRY_INTERVAL | | 10 | integer | true |

Run:
```
docker-compose --env-file ./docker.env up -d --build
```

Api docs will now be accessible at **{host}:{APP_PORT}/**.

Down containert with command:
```
docker-compose --env-file ./docker.env down
```

**Important:** This `docker-compose.yml` is configured for local testing only, and is _not_ intended for production use.

### Debugging

To tail the logs from the Docker containers in realtime, run:

```bash
docker-compose logs -f
```

## Setup with Virtualenv

You can run the site locally without setting up Vagrant or Docker and simply use Virtualenv, which is the [recommended installation approach](https://docs.djangoproject.com/en/3.2/topics/install/#install-the-django-code) for Django itself.

#### Dependencies

- Python 3.6, 3.7, 3.8 or 3.9
- [Virtualenv](https://virtualenv.pypa.io/en/stable/installation/)
- [VirtualenvWrapper](https://virtualenvwrapper.readthedocs.io/en/latest/install.html) (optional)
- [NodeJs and npm cli](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) 

### Installation

#### Creating your Virtualenv

With [PIP](https://github.com/pypa/pip) and [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/)
installed, run:

    mkvirtualenv nsravenv
    python --version

or 

With [PIP](https://github.com/pypa/pip) and [python3](https://docs.python.org/3/library/venv.html)
installed, run:

    python3 -m venv /path/to/new/virtual/environment

Confirm that this is showing a compatible version of Python 3.x. If not, and you have multiple versions of Python installed on your system, you may need to specify the appropriate version when creating the virtualenv:

    deactivate
    rmvirtualenv 
    mkvirtualenv nsravenv --python=python3.9
    python --version

Now we're ready to set up the nsra project itself:

    cd ~/dev [or your preferred dev directory]
    git clone https://github.com/eliblurr/nsra.git
    cd nsra
    npm install
    source /path/to/venv/bin/activate
    pip install -r requirements/base.txt

Next, we'll set up our local environment variables. We use [django-dotenv](https://github.com/jpadilla/django-dotenv)
to help with this. It reads environment variables located in a file name `.env` in the top level directory of the project. The only variable we need to start is `DJANGO_SETTINGS_MODULE`:

    $ cp nsra/settings/local.py.example nsra/settings/local.py
    $ mv env.example .env [update enviromental variables and change accordingly]
    
allowed environment variables `KEYWORDS`=`VALUES`:

| KEYWORDS | VALUES | DEFAULT VALUE | VALUE TYPE | IS REQUIRED | ENVIRONMENT |
| :------------ | :---------------------: | :------------------: | :------------------: | :------------------: | :------------------: |
| ENVIRONMENT | dev or prod | dev | string | true | all |
| DJANGO_SUPERUSER_USERNAME | | admin | string | false | all |
| DJANGO_SUPERUSER_PASSWORD | | changeme | string | false | all |
| DEBUG | on or off | on | string | false | production |
| SECRET_KEY | | | string | string | production |
| DJANGO_SECURE_SSL_REDIRECT | on or off | off | string | false | production |
| ADMINS | .e.g. admin,admin@admin.com;admin2,admin2@admin.com; | | username,email; | true | production |
| ALLOWED_HOSTS | | * | urls | false | production |
| BASE_URL | .e.g. http://host1.com | http://localhost | url | true | production |
| EMAIL_HOST | | | url | true | production |
| EMAIL_PORT | | | integer | true | production |
| EMAIL_USE_TLS | true or false | | bool | true | production |
| EMAIL_USE_SSL | true or false | | bool | true | production |
| EMAIL_HOST_USER | | | string | true | production |
| EMAIL_HOST_PASSWORD | | | string | true | production |
| EMAIL_SSL_CERTFILE | | | string | false | production |
| EMAIL_SSL_KEYFILE | | | string | false | production |
| EMAIL_TIMEOUT | | | integer | false | production |
| EMAIL_USE_LOCALTIME | true or false | false | bool | false | production |
| EMAIL_SUBJECT_PREFIX | | | string | false | production |
| CACHE_URL | | | url | false | production |
| MEDIA_BUCKET_SERVICE | gs or aws | | string | false | production |
| GS_PROJECT_ID | | | string | true if MEDIA_BUCKET_SERVICE==gs else false | production |
| GS_BUCKET_NAME | | | string | true if MEDIA_BUCKET_SERVICE==gs else false | production |
| AWS_REGION | | | url | true if MEDIA_BUCKET_SERVICE==aws else false | production |
| AWS_ACCESS_KEY_ID | | | string | true if MEDIA_BUCKET_SERVICE==aws else false | production |
| AWS_SESSION_TOKEN | | | string | true if MEDIA_BUCKET_SERVICE==aws else false | production |
| AWS_SECRET_ACCESS_KEY | | | string | true if MEDIA_BUCKET_SERVICE==aws else false | production |
| AWS_STORAGE_BUCKET_NAME | | | string | true if MEDIA_BUCKET_SERVICE==aws else false | production |
| ELASTICSEARCH_URL | | | url | false | production |
| ELASTICSEARCH_PORT | | 9200 | integer | true if ELASTICSEARCH_URL is set else false | production |
| ELASTICSEARCH_USE_SSL | on or off | | url | true if ELASTICSEARCH_URL is set else false | production |
| ELASTICSEARCH_VERIFY_CERTS | on or off | | url | true if ELASTICSEARCH_URL is set else false | production |
| FILE_LOG_LEVEL | | ERROR | string | false | production |
| MAIL_LOG_LEVEL | | CRITICAL | string | false | production |
| CACHE_URL | | | url | false | production |
| DATABASE_URL | | | url | true | production |

To set up your database without initial data, run the following commands in shell:

    chmod +x init.sh     
    ./init.sh

To set up your database with initial data, run the following commands in shell:

    chmod +x init.sh  
    ./init.sh -z load

Start app server with:

    ./manage.py runserver

Log into the admin with the credentials `admin / changeme` or `values for newly set DJANGO_SUPERUSER_USERNAME and DJANGO_SUPERUSER_PASSWORD`.

## Deploy to Heroku

If you want a publicly accessible site, use [Heroku's](https://heroku.com) one-click deployment solution to the free 'Hobby' tier:

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/eliblurr/nsra)

If you do not have a Heroku account, clicking the above button will walk you through the steps
to generate one. At this point you will be presented with a screen to configure your app. For our purposes,
we will accept all of the defaults and click `Deploy`. The status of the deployment will dynamically
update in the browser. Once finished, click `View` to see the public site.

Log into the admin with the credentials `admin / changeme`.

To prevent the site from regenerating a new Django `SECRET_KEY` each time Heroku restarts your site, you should set
a `DJANGO_SECRET_KEY` environment variable in Heroku using the web interace or the [CLI](https://devcenter.heroku.com/articles/heroku-cli). If using the CLI, you can set a `SECRET_KEY` like so:

    heroku config:set DJANGO_SECRET_KEY=changeme

To learn more about Heroku, read [Deploying Python and Django Apps on Heroku](https://devcenter.heroku.com/articles/deploying-python).

### Storing Wagtail Media Files on AWS S3

If you have deployed the site to Heroku or via Docker, you may want to perform some additional setup. Heroku uses an
[ephemeral filesystem](https://devcenter.heroku.com/articles/dynos#ephemeral-filesystem), and Docker-based hosting
environments typically work in the same manner. In laymen's terms, this means that uploaded images will disappear at a
minimum of once per day, and on each application deployment. To mitigate this, you can host your media on S3.

This documentation assumes that you have an AWS account, an IAM user, and a properly configured S3 bucket. These topics
are outside of the scope of this documentation; the following [blog post](https://wagtail.org/blog/amazon-s3-for-media-files/)
will walk you through those steps.

This site comes preconfigured with a production settings file that will enable S3 for uploaded media storage if
`AWS_STORAGE_BUCKET_NAME` is defined in the shell environment. All you need to do is set the following environment
variables. If using Heroku, you will first need to install and configure the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli). Then, execute the following commands to set the aforementioned environment variables:

    heroku config:set AWS_STORAGE_BUCKET_NAME=changeme
    heroku config:set AWS_ACCESS_KEY_ID=changeme
    heroku config:set AWS_SECRET_ACCESS_KEY=changeme

Do not forget to replace the `changeme` with the actual values for your AWS account. If you're using a different hosting
environment, set the same environment variables there using the method appropriate for your environment.

Once Heroku restarts your application or your Docker container is refreshed, you should have persistent media storage!

Running `./manage.py load_initial_data` will copy local images to S3, but if you set up S3 after you ran it the first
time you might need to run it again.

## Deploy as AWS-EC2 Instance

To be included

# Contributing

If you're a Python or Django developer, fork the repo and get stuck in! If you'd like to get involved you may find our [contributing guidelines](https://github.com/eliblurr/nsra/blob/master/contributing.md) a useful read.

### Preparing this archive for distribution

If you change content or images in this repo and need to prepare a new fixture file for export, do the following on a branch:

`./manage.py dumpdata --natural-foreign --indent 2 -e auth.permission -e contenttypes -e wagtailcore.GroupCollectionPermission -e wagtailimages.filter -e wagtailcore.pagerevision -e wagtailimages.rendition -e sessions > nsra/base/fixtures/site.json`

Please optimize any included images to 1200px wide with JPEG compression at 60%. Note that `media/images` is ignored in the repo by `.gitignore` but `media/original_images` is not. Wagtail's local image "renditions" are excluded in the fixture recipe above.

Make a pull request to https://github.com/eliblurr/nsra.git

# Other notes

### Note on search

Because we can't (easily) use ElasticSearch for this site, we use wagtail's native DB search.
However, native DB search can't search specific fields in our models on a generalized `Page` query.
So for site purposes ONLY, we hard-code the model names we want to search into `search.views`, which is
not ideal. In production, use ElasticSearch and a simplified search query, per
[https://docs.wagtail.org/en/stable/topics/search/searching.html](https://docs.wagtail.org/en/stable/topics/search/searching.html).

### Sending email from the contact form

The following setting in `base.py` and `production.py` ensures that live email is not sent by the contact form.

`EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'`

In production on your own site, you'll need to change this to:

`EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'`

and configure [SMTP settings](https://docs.djangoproject.com/en/3.2/topics/email/#smtp-backend) appropriate for your email provider.

### Ownership of content

All content in this site is public domain. Textual content in this project is either sourced from Wikipedia or is lorem ipsum. All images are from either Wikimedia Commons or other copyright-free sources.

