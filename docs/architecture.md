# Architecture notes

The following records changes to the architecture we have explored through this firebreak project, with the aim of making the Data-as-a-product API easier to build out and maintain.

## Single API service

Previously, we had each API endpoint implemented as an independently deployable lambda, and routing handled by AWS API gateway.

Ideally we want to have a consolidated API service that we can deploy and test as one artefact. This should reduce deployment complexity and make it possible to test more of the API locally.

## FastAPI

We want to make use of a python framework to speed up development. We chose to investigate FastAPI due to ease of setup and it being well supported.

Relevant resources:

- [Create and deploy a reliable data ingestion service with FastAPI, SQLModel and Dramatiq](https://www.francoisvoron.com/blog/create-deploy-reliable-data-ingestion-service-fastapi-sqlmodel-dramatiq)

Alternatives:

- LiteStar
- Django RF
- Sanic
- Flask

Example app deployed onto MOJ Cloud Platform: [laa-court-data-api](https://github.com/ministryofjustice/laa-court-data-api/tree/main)

### Pydantic models

FastAPI is built on top of Pydantic, which makes validation very simple.

We no longer need to manage JSON schemas, since we can generate them from the models.

## Technology for metadata store

We are operating under the assumption that we want to maintain control over our metadata store,
rather than tightly coupling it to our choice of catalogue.

Previously we have been using an S3 bucket & JSON for this, but we think switching to a database would make
create/read/update/delete operations simpler.

We may also want to run ad-hoc statistics queries or visualise the health of the platform on a dashboard.

Possibilities to explore:

- PostgreSQL
- DynamoDB
- Redis

## API design considerations

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

## Hosting concerns

The API could be hosted on the Cloud Platform, rather than the Modernisation Platform.

We will need to consider

- how this affects observability
- connectivity to other components of the data platform

### Should data operations be part of this service?

We're not sure yet!

We are using presigned S3 URLs as the ingestion mechanism because it provides an easy
way to perform a single upload of files up to 5GB.
