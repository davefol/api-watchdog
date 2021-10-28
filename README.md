# API Watchdog

## Usage
```
api-watchdog discover path/to/test/files
```
Will output the abbreviated result of the tests to stdout.

```
api-watchdog discover --email path/to/test/files
```
Will email the results of the tests to the relevant addresses
(as determined by the `email_to=` field of the test. Test results
are grouped so that only one email per address is sent per run.

Whjen using the CLI, these environment variables must be set to email results
- MAILGUN_API_URL
- MAILGUN_API_TOKEN
- MAILGUN_FROM

```
api-watchdog discover -o results_file.json path/to/test/files
```
Will serialize the `WatchdogResultGroup` object to the path specified
by the `-o` flag. 

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

