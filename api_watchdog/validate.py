from enum import Enum
from typing import Any
from pydantic import ValidationError as PydanticValidationError

from api_watchdog.integrations import trapi

class ValidationError(Exception):
    """Raised when an object fails to validate"""

class UnknownValidationTypeError(Exception):
    """Raised when an unknown ValidationType is provided"""

class UnsupportedValidationTypeError(Exception):
    """
    Raised when an unsupported ValidationType is provided

    eg. using a trapi.* ValidationType when the library
    is not installed with TRAPI

    """

def validate_none(x):
    """Test whether object is None and returns none"""
    if x is not None:
        raise ValidationError

class ValidationType(Enum):
    # Plain JSON types
    String = "string"
    Int    = "int"
    Float  = "float"
    Object = "object"
    Bool   = "bool"
    Null   = "null"

    # TRAPI types
    TrapiKnowledgeGraph     = "trapi.knowledge_graph"
    TrapiNode               = "trapi.node"
    TrapiEdge               = "trapi.edge"
    TrapiQueryGraph         = "trapi.query_graph"
    TrapiQNode              = "trapi.q_node"
    TrapiQEdge              = "trapi.q_edge"
    TrapiQueryConstraint    = "trapi.query_constraint"
    TrapiResult             = "trapi.result"
    TrapiNodeBinding        = "trapi.node_binding"
    TrapiEdgeBinding        = "trapi.edge_binding"
    TrapiMessage            = "trapi.message"
    TrapiQuery              = "trapi.query"
    TrapiResponse           = "trapi.response"
    TrapiAsyncQuery         = "trapi.async_query"
    TrapiOperation          = "trapi.operation"
    TrapiWorkflow           = "trapi.workflow"
    TrapiAttribute          = "trapi.attribute"
    TrapiBiolinkEntity      = "trapi.biolink_entity"
    TrapiBiolinkPredicate   = "trapi.biolink_predicate"
    TrapiLogEntry           = "trapi.log_entry"
    TrapiLogLevel           = "trapi.log_level"
    TrapiMetaEdge           = "trapi.meta_edge"
    TrapiMetaNode           = "trapi.meta_node"
    TrapiMetaKnowledgeGraph = "trapi.meta_knowledge_graph"
    TrapiMetaAttribute      = "trapi.meta_attribute"

validation_registry = {
    ValidationType.String                 : str                     ,
    ValidationType.Int                    : int                     ,
    ValidationType.Float                  : float                   ,
    ValidationType.Object                 : dict                    ,
    ValidationType.Bool                   : bool                    ,
    ValidationType.Null                   : validate_none           ,
    ValidationType.TrapiKnowledgeGraph    : trapi.KnowledgeGraph    ,
    ValidationType.TrapiNode              : trapi.Node              ,
    ValidationType.TrapiEdge              : trapi.Edge              ,
    ValidationType.TrapiQueryGraph        : trapi.QueryGraph        ,
    ValidationType.TrapiQNode             : trapi.QNode             ,
    ValidationType.TrapiQEdge             : trapi.QEdge             ,
    ValidationType.TrapiQueryConstraint   : trapi.QueryConstraint   ,
    ValidationType.TrapiResult            : trapi.Result            ,
    ValidationType.TrapiNodeBinding       : trapi.NodeBinding       ,
    ValidationType.TrapiEdgeBinding       : trapi.EdgeBinding       ,
    ValidationType.TrapiMessage           : trapi.Message           ,
    ValidationType.TrapiQuery             : trapi.Query             ,
    ValidationType.TrapiResponse          : trapi.Response          ,
    ValidationType.TrapiAsyncQuery        : trapi.AsyncQuery        ,
    ValidationType.TrapiOperation         : trapi.Operation         ,
    ValidationType.TrapiWorkflow          : trapi.Workflow          ,
    ValidationType.TrapiAttribute         : trapi.Attribute         ,
    ValidationType.TrapiBiolinkEntity     : trapi.BiolinkEntity     ,
    ValidationType.TrapiBiolinkPredicate  : trapi.BiolinkPredicate  ,
    ValidationType.TrapiLogEntry          : trapi.LogEntry          ,
    ValidationType.TrapiLogLevel          : trapi.LogLevel          ,
    ValidationType.TrapiMetaEdge          : trapi.MetaEdge          ,
    ValidationType.TrapiMetaNode          : trapi.MetaNode          ,
    ValidationType.TrapiMetaKnowledgeGraph: trapi.MetaKnowledgeGraph,
    ValidationType.TrapiMetaAttribute     : trapi.MetaAttribute     ,
}

def validate(x: Any, validation_type: ValidationType):
    """
    Converts object into corresponding type.

    Raises ValidationError if the object fails to validate
    """
    try:
        cls = validation_registry[validation_type]
    except KeyError as e:
        raise UnknownValidationTypeError from e

    try:
        if trapi.istrapi(cls):
            return cls.parse_obj(x)
        else:
            return cls(x) if x is not None else None
    except AttributeError as e:
        raise UnsupportedValidationTypeError(
            f"{validation_type} support has not been installed.") from e
    except TypeError as e:
        raise ValidationError(f"{x} is not a valid {validation_type}") from e
    except PydanticValidationError as e:
        raise ValidationError(f"{x} is not a valid {validation_type}") from e

