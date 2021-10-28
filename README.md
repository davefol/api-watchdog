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

## WatchdogTest format
The main way you'll interface with API Watchdog is through `WatchdogTest`s.
Each `WatchdogTest` has
- name (str): The name of the test
- target (url): The endpoint that the test targets
- expectations (Array[Expectation]): A list of requirements that the response must meet for the test to pass.
- payload (object): The json passed to the endpoint.

## Expectation format
An `Expectation` describes where to find a piece of data in the response and what that piece of data should be in order for the test to pass.
Each `Expectation` has

- selector (jq program): A string describing a jq program that selects the one or more elements to test against
- value (Any): a value to test equality against
- validation_type (ValidationType): An API Watchdog validation type used to validate the value/response. The value/response will be implicitly converted to this type. For example, if you specify 'float' and the value is an integer it will be implicitly converted to a float.

The selector format is a string that is a [jq program](https://stedolan.github.io/jq/). This allows for rich selection capabilities. 
For example:

```
    {
      "selector": ".message.knowledge_graph.nodes[\"MONDO:0005148\"].name",
      "value": "type 2 diabetes mellitus",
      "validation_type": "string"
    },
```

Is an `Expectation` that checks if a node is present in the knowledge graph of a TRAPI response. 

The possible validation types are 
- "string",
- "int",
- "float",
- "object",
- "bool",
- "null",
- "trapi.knowledge_graph",
- "trapi.node",
- "trapi.edge",
- "trapi.query_graph",
- "trapi.q_node",
- "trapi.q_edge",
- "trapi.query_constraint",
- "trapi.result",
- "trapi.node_binding",
- "trapi.edge_binding",
- "trapi.message",
- "trapi.query",
- "trapi.response",
- "trapi.async_query",
- "trapi.operation",
- "trapi.workflow",
- "trapi.attribute",
- "trapi.biolink_entity",
- "trapi.biolink_predicate",
- "trapi.curie",
- "trapi.log_entry",
- "trapi.log_level",
- "trapi.meta_edge",
- "trapi.meta_node",
- "trapi.meta_knowledge_graph",
- "trapi.meta_attribute"


## What it is
An API monitoring utility that aspires to support:
- [ ] Validation
- [ ] Continuous Integration
- [ ] Multiple input and output formats
- [ ] Test discovery / minimal configuration

## What it is not
- A way to regularly schedule tests against an endpoint, eg. [cron](https://en.wikipedia.org/wiki/Cron), [celery](https://docs.celeryproject.org/en/stable/getting-started/introduction.html)
- A way to specify api schemas eg. [marshmallow](https://marshmallow.readthedocs.io/en/stable/), [pydantic](https://pydantic-docs.helpmanual.io/) 

