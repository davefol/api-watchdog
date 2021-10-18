from pydantic import BaseModel
try:
    from reasoner_pydantic.message import Message as TrapiMessage
    # TrapiMessage is already a Pydantic model so configuration is a noop
except ImportError:
    class TrapiMessage(BaseModel):
        def __init__(self, *args, **kwargs):
            raise NotImplementedError("Must install with 'TRAPI' extension")

