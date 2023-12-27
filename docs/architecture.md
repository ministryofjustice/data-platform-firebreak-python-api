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

- Integrating an ORM (Object-relational mapper)
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

Previously we have been using an S3 bucket & JSON as the metadata store.
S3 is not designed to function as a database, and we think
switching to a database would make CRUD operations (Create / Read / Update / Delete) simpler.

We may also want to run ad-hoc statistics queries
or visualise the health of the platform on a dashboard, which we can't do directly with S3.

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

Alembic is a tool written by the same author to manage database migrations.
It helps you version your database schema so that
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

## Cloud Platform

We're hosting this proof of concept in MOJ's [Cloud Platform](https://user-guide.cloud-platform.service.justice.gov.uk/),
because it's a self contained service designed for hosting apps on a centralised platform.
This means that there are modules already available that provide the functionality
we need for hosting an api, as well as other internal apis hosted there that we can learn from.

All of the configuration can be injected via environment variables.

Currently, this proof of concept is not talking to the rest of the Data Platform.
We would need connectivity to the public data catalogue to make our metadata visible to consumers,
and connectivity to the glue catalogue to expose metadata to the ingestion pipeline.

## New API design

We have explored a different design for the API resources based on [Azure's best practices guide](https://learn.microsoft.com/en-us/azure/architecture/best-practices/api-design).

Some things that are different in this version:

1. All resources have public-facing IDs that can be used to fetch the resource e.g. dp:hmpps_use_of_force:v1.0 and dp:hmpps_use_of_force:v1.0:statements.

2. All versions of data products and schemas are addressable via GET, PUT
   and DELETE requests, not just the latest version.
   (This idea is questionable; DELETE and PUT semantics only make sense against
   the latest version)

3. We added a user-friendly mechanism for making operations idempotent

[Proposed design spreadsheet](https://docs.google.com/spreadsheets/d/1SF0m4j-_NSLD6yyuJizZC0F06jHPkAvLWheuLeHORJk/edit#gid=626736695)

## Do we still need API gateway?

Currently AWS API gateway handles various concerns:

- HTTPS
- Authentication/Authorization
- Documentation hosting
- Web Application Firewall (WAF)
- Rate limiting
- Logging and monitoring
- Versioning / lifecycle management

Some of this could be handled by the python framework, or a load balancer.

Current state of concerns:

- HTTPS (:question:)
- Authentication/Authorisation
  (:heavy_check_mark: - handled by [fastapi-azure-auth](https://intility.github.io/fastapi-azure-auth/),
  a python library for handling Azure Active Directory auth flow)
- Documentation hosting (:heavy_check_mark: - handled by FastAPI)
- Web Application Firewall (WAF)
  (:heavy_check_mark: - [available via Cloud Platform](https://user-guide.cloud-platform.service.justice.gov.uk/documentation/networking/modsecurity.html))
- Rate limiting (:question:)
- Logging and monitoring
  (:heavy_check_mark: - [handled through Cloud Platform](https://user-guide.cloud-platform.service.justice.gov.uk/#monitoring))
- Versioning / lifecycle management (:question:)

## Authentication and authorisation

Data Platform are moving towards using Azure Active Directory (AAD, also now known as Entra ID)
as the central authentication and authorisation mechanism for Data Platform.
For this api, one of the considerations for the auth flow is that the Swagger UI (the `/docs` endpoint)
is a [single-page application](https://learn.microsoft.com/en-us/entra/identity-platform/v2-app-types#single-page-apps),
which has security implications as the application cannot securely store a client secret
without risk of exposing the secret and compromising the app.

Instead, Microsoft recommends using the OAuth 2.0 authorization code grant flow, which
_"enables a client application to obtain authorized access to protected resources like web APIs"_

We are using the [fastapi-azure-auth](https://intility.github.io/fastapi-azure-auth/)
python library to handle the integration of this auth flow (_PKCE with authorisation code grant_)
with FastAPI.

The registration process is very clearly explained in the [tutorial documentation for the library](https://intility.github.io/fastapi-azure-auth/single-tenant/azure_setup).
It involves [registering two apps in the Azure Active Directory Portal](https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps)
(one for the api, one for the swagger UI),
adding the requisite config settings to the app, and then testing out an endpoint.

We can secure any endpoints behind this authentication flow [by adding a requirement in the endpoint definition](https://intility.github.io/fastapi-azure-auth/single-tenant/fastapi_configuration#adding-authentication-to-our-view).

We can also [specify requirements for the user for any specific endpoint](https://intility.github.io/fastapi-azure-auth/usage-and-faq/locking_down_on_roles)
(e.g. has a specific role associated with their user, or belongs to a specific group).
For example requiring a 'Data Producer' or 'Data Steward' role for a registration endpoint.

Any direct usage of the api not going through the swagger UI should use the
[Client Credential Flow](https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-client-creds-grant-flow),
as described in [the fastapi-azure-auth docs](https://intility.github.io/fastapi-azure-auth/usage-and-faq/calling_your_apis_from_python).

Our apps required admin approval due to settings within AAD.

## Should data operations be part of the same service as the metadata store?

We're not sure yet!

We are using presigned S3 URLs as the ingestion mechanism because it provides an easy
way to perform a single upload of files up to 5GB.

We did not bring this into the proof of concept, but it could be exposed via the same API.
However, we are assuming that the ingestion pipeline itself will run within the modernisation platform environment.
