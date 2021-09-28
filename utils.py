from inspect import Parameter, signature
from secrets import token_urlsafe
from fastapi import Form

def gen_code(nbytes=8):
    return token_urlsafe(nbytes)

def as_form(cls):
    form = [
        Parameter( model_field.alias,
            Parameter.POSITIONAL_ONLY,
            default=Form(model_field.default) if not model_field.required else Form(...),
            annotation=model_field.outer_type_
        ) for _ ,model_field  in cls.__fields__.items()
    ]
    def _cls_(**data):
        return cls(**data)
    _cls_.__signature__ = signature(_cls_).replace(parameters=form)
    setattr(cls, 'as_form', _cls_)
    return cls

def is_pydantic(obj: object):
    """Checks whether an object is pydantic."""
    return type(obj).__class__.__name__ == "ModelMetaclass"

def schema_to_model(schema, exclude_unset=False):
    """Iterates through pydantic schema and parses nested schemas
    to a dictionary containing SQLAlchemy models.
    Only works if nested schemas have specified the Meta.model."""
    parsed_schema = dict(schema)
    try:
        for k,v in parsed_schema.items():
            if isinstance(v, list) and len(v) and is_pydantic(v[0]):
                parsed_schema[k] = [item.Meta.model(**schema_to_model(item)) for item in v]
            elif is_pydantic(v):
                parsed_schema[k] = v.Meta.model(**schema_to_model(v))
    except AttributeError:
        raise AttributeError(f"found nested pydantic model in {schema.__class__} but Meta.model was not specified.")
    
    if exclude_unset:
        parsed_schema = {k: v for k, v in parsed_schema.items() if v is not None}
    
    return parsed_schema