import jwt, shutil, logging, pathlib, xattr, os, config
from datetime import timedelta, datetime, date
from config import JWT_ALGORITHM, LOG_ROOT
from babel.numbers import format_currency
from inspect import Parameter, signature
from math import ceil, floor, log2
from secrets import token_urlsafe
from sqlalchemy import inspect
from fastapi import Form
from passlib import pwd

def instance_changes(instance):
    state = inspect(instance)
    changes = {}

    for attr in state.attrs:
        hist = attr.load_history()

        if not hist.has_changes():
            continue

        # hist.deleted holds old value
        # hist.added holds new value
        changes[attr.key] = hist.added

    return changes

def parse_activity_meta(obj, meta):
    for k,v in meta.items():
        if isinstance(v, list):
            val = ''
            for v in v:
                attr = v.split('.')
                tmp = getattr(obj, attr[0])
                for x in attr[1:]:
                    tmp = getattr(tmp, x)
                val+=f' {tmp}'
            meta[k]=val.strip()
        else:
            attr = v.split('.')
            tmp = getattr(obj, attr[0])
            for x in attr[1:]:
                tmp = getattr(tmp, x)
            meta[k]=str(tmp)
    return meta

def logger(path, e, level:str): 
    " path should be __name__ "
    " e.g.logger(__name__, 'some error', 'error')"

    
    def set_entry(level:str):
        file = f"{date.today().strftime('%Y-%m-%d')}.log"
        path = os.path.join(LOG_ROOT, file)
        file = xattr.xattr(path)
        entry = xattr.getxattr(path, level) if level in file.keys() else 0
        xattr.setxattr(path, level, f'{int(entry)+1}'.encode())
    

    logger = logging.getLogger(f'asset.{path}')
    if level.lower()=='info':logger.info(e)
    elif level.lower()=='debug':logger.debug(e)
    elif level.lower()=='error':logger.error(e)
    elif level.lower()=='warning':logger.warning(e)
    elif level.lower()=='critical':logger.critical(e)
    
    try:set_entry(level.lower())
    except Exception as e:logger.critical(e)

def create_jwt(data:dict, exp:timedelta=None):
    data.update({'exp':datetime.utcnow() + timedelta(minutes=exp if exp else config.settings.DEFAULT_TOKEN_DURATION_IN_MINUTES)})
    return jwt.encode(data, config.settings.SECRET, algorithm=JWT_ALGORITHM)

def decode_jwt(token):
    return jwt.decode(token, config.settings.SECRET, algorithms=[JWT_ALGORITHM])

def gen_code(nbytes=8):
    return token_urlsafe(nbytes)

def gen_hex():
    return pwd.genword(entropy=128, charset="hex")

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

def http_exception_detail(loc=None, msg=None, type=None):
    detail = {}
    if loc:
        detail.update({"loc":loc if loc.__class__ in [list, set, tuple] else [loc]})
    if type:
        detail.update({"type":type})
    if msg:
        detail.update({"msg":msg})
    return [detail]

def v_2n(n):
    assert ceil(log2(n)) == floor(log2(n)), f'{n} is not a power 2'
    return n

def delete_path(path):
    try:
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
    except OSError as e:
        logger = logging.getLogger("eAsset.main")
        logger.error("Error: %s - %s." % (e.filename, e.strerror))

def timestamp_to_datetime(timestamp):
    return datetime.fromtimestamp(timestamp)

def money(currency:str, amount:float, locale:str=None):
    if locale:
        format_currency(amount, currency, locale=locale)
    return format_currency(amount, currency)

def db_url():
    '''
        current version of sqlalchemy does not support [postgres]:// 
        hence change to postgresql to accomodate
    '''
    db_url = config.settings.DATABASE_URL
    if db_url.split(':', 1)[0] in ['postgres']:
        db_url = 'postgresql:'+db_url.split(':', 1)[1]
    return db_url

def generator(keys):
    prev_key = None
    for key in keys:
        yield key
        prev_key = key

def raise_exc(loc=None, msg=None, type=None):
    detail = {}
    if loc:
        detail.update({"loc":loc if loc.__class__ in [list, set, tuple] else [loc]})
    if msg:
        detail.update({"msg":msg})
    if msg:
        detail.update({"type":type})
    return [detail]

def urljoin(*args):
    """
    Joins given arguments into an url. Trailing but not leading slashes are
    stripped for each argument.
    """

    return "/".join(map(lambda x: str(x).rstrip('/').lstrip('/'), args))

from fastapi import Query

today = date.today()
sum_ls = lambda ls : sum(ls)
today_str =  lambda: today.strftime("%Y/%m/%d")
r_fields = lambda model : Query(None, regex=f"({'|'.join([_[0] for _ in model.c()])})$") # result fields
file_ext = lambda filename : pathlib.Path(filename).suffix

def act_url(base_url, id, userType):
    return f"""{base_url}{config.settings.ACCOUNT_ACTIVATION_PATH}?token={create_jwt(data={'id':id, "userType":userType},exp=timedelta(minutes=config.settings.ACTIVATION_TOKEN_DURATION_IN_MINUTES))}"""