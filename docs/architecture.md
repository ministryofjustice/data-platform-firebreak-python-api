# Architecture notes

The following records changes to the architecture we have explored through this firebreak project, with the aim of making the Data-as-a-product API easier to build out and maintain.

## Single API service

Previously, we had each API endpoint implemented as an independently deployable lambda, and routing handled by AWS API gateway.

We have consolidated these into a single API service that we can deploy and test as one artefact. This should reduce deployment complexity and make it easier to develop locally. E.g. we can run all the tests in one
go and be confident that the API endpoints work together consistently.

## FastAPI / Pydantic

We wanted to make use of a python framework to speed up development. We chose to investigate FastAPI due to ease of setup and it being well supported.

FastAPI is built on top of Pydantic, which makes validation very simple. We no longer need to manage JSON schemas, since we can generate them from the Pydantic models.

Things that worked well out of the box:

- Serializing and deserializing JSON responses
- Input validation
- Generating OpenAPI spec
- Testing

Things that required a bit more configuration:

- Integrating an ORM
- Integrating auth

Relevant resources:

- [Create and deploy a reliable data ingestion service with FastAPI, SQLModel and Dramatiq](https://www.francoisvoron.com/blog/create-deploy-reliable-data-ingestion-service-fastapi-sqlmodel-dramatiq)
- [FastAPI introductory tutorials](https://fastapi.tiangolo.com/learn/)
- [Pydantic getting started guide](https://docs.pydantic.dev/latest/)
- Example app deployed onto MOJ Cloud Platform: [laa-court-data-api](https://github.com/ministryofjustice/laa-court-data-api/tree/main)

Note that Pydantic has recently been updated to version 2.0, so some resources may be out of date.

Alternatives:

- LiteStar
- Django Rest Framework
- Sanic
- Flask

## PostgreSQL

We are operating under the assumption that we want to maintain control over our metadata store,
rather than tightly coupling it to our choice of data catalogue.

Previously we have been using an S3 bucket & JSON as the metadata store, but S3 is not designed to function as a database, and we think switching to a database would make
create/read/update/delete operations simpler.

We may also want to run ad-hoc statistics queries or visualise the health of the platform on a dashboard, which we can't do directly with S3.

We decided to use PostgreSQL because it's Open Source and supports SQL.
We can use any SQL ORM to simplify the persistence code.

We've made use of JSON columns for the column definitions, to simplify
CRUD operations on schema metadata.

Alternatives:

- Redis
- DynamoDB

## SQLAlchemy and Alembic

SQLAlchemy is a mature ORM (Object-relational mapper).
It maps database tables to Python objects and generates SQL for you.

Alembic is a tool written by the same author to manage database migrations. It helps you version your database schema so that
you can automatically bring the schema up to date when deploying
the application.

Resources:

- [SQLAlchemy ORM quickstart](https://docs.sqlalchemy.org/en/20/orm/quickstart.html)
- [SQLAlchemy querying guide](https://docs.sqlalchemy.org/en/20/orm/queryguide/index.html)
- [Patterns and Practices for using SQLAlchemy 2.0 with FastAPI](https://chaoticengineer.hashnode.dev/fastapi-sqlalchemy)
- [FastAPI with Async SQLAlchemy, SQLModel, and Alembic](https://testdriven.io/blog/fastapi-sqlmodel/)
- [Alembic tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)

Alternatives:

- SQLModel (built on top of SQLAlchemy)
- Django ORM
- SQLAlchemy core without the ORM
- Plain SQL

## Cloud platform

We're hosting this proof of concept in the MOJ cloud platform, because it's
a relatively self contained service that can run in a Kubernetes cluster, so there
is no need for us to write our own terraform.

All of the configuration can be injected via environment variables.

Currently, this proof of concept is not talking to the rest of the data platform.
We would need connectivity to the public data catalogue to make our metadata visible to consumers, and connectivity to the glue catalogue to expose metadata to the ingestion pipeline.

## New API design

We have explored a different design for the API resources based on [Azure's best practices guide](https://learn.microsoft.com/en-us/azure/architecture/best-practices/api-design).

Some things that are different in this version:

1. All resources have public-facing IDs that can be used to fetch the resource e.g. dp:hmpps_use_of_force:v1.0 and dp:hmpps_use_of_force:v1.0:statements.

2. All versions of data products and schemas are addressable, not just the latest version

3. We added a user-friendly mechanism for making operations idempotent

[Proposed design spreadsheet](https://docs.google.com/spreadsheets/d/1SF0m4j-_NSLD6yyuJizZC0F06jHPkAvLWheuLeHORJk/edit#gid=626736695)

## Do we still need API gateway?

Currently AWS API gateway handles various concerns:

- HTTPS
- Authentication/Authorization
- Documentation hosting
- Web application firewall
- Rate limiting
- Logging and monitoring
- Versioning / lifecycle management

Some of this could be handled by the python framework, or a load balancer.

## Should data operations be part of the same service as the metadata store?

We're not sure yet!

We are using presigned S3 URLs as the ingestion mechanism because it provides an easy
way to perform a single upload of files up to 5GB.

We did not bring this into the proof of concept, but it could be exposed via the same API. However, we are assuming that the ingestion pipeline itself will run within the modernisation platform environment.
