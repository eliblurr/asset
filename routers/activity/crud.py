from config import STATIC_ROOT
import json, os, logging
from . import models
from cls import CRUD

activity = CRUD(models.Activity)
logger = logging.getLogger("eAsset.routers.activity")
path = os.path.join(STATIC_ROOT, 'json/activity.json')

'''
target = {
    "key":{
        "user_id":1,
        "value":"title"
    }
}
'''

async def get_message(key:str, op:str, target:dict):
    try:
        with open(path) as f:
            data = json.load(f)
        data = data[key][op]
        if set(target.keys())!=set([n for _,n,_,_ in Formatter().parse(data) if n]):
            raise ValueError('key mismatch b/n target and message')        
        return ActivityBase(msg=data[key][op], meta=target)
    except KeyError:
        raise KeyError(f'could not find message for {key}.{op}')
    except Exception as e:
        logger.critical(f"{e.__class__}: {e}")
    finally:
        f.close()

activity.get_message = get_message