# API Watchdog

## Installation
API watchdog handles validation support through extra requirements.
This means that to install it with TRAPI validation you invoke
```
pip install api-watchdog[TRAPI]
```

If you are using `zsh` you will run affoul of bracket globbing and should use
```
pip install 'api-watchdog[TRAPI]'
```

See this [stackoverflow question](https://stackoverflow.com/questions/30539798/zsh-no-matches-found-requestssecurity) for context.

Available extensions are:
- TRAPI

If you do not want any validation support you can use the bare `pip install api-watchdog` command.

## What it is
An API monitoring utility that aspires to support:
- [ ] Validation
- [ ] Continuous Integration
- [ ] Multiple input and output formats
- [ ] Test discovery / minimal configuration

## What it is not
- A way to regularly schedule tests against an endpoint, eg. [cron](https://en.wikipedia.org/wiki/Cron), [celery](https://docs.celeryproject.org/en/stable/getting-started/introduction.html)
- A way to specify api schemas eg. [marshmallow](https://marshmallow.readthedocs.io/en/stable/), [pydantic](https://pydantic-docs.helpmanual.io/) 

