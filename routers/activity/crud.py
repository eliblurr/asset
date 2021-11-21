from config import STATIC_ROOT
import json, os, logging
from . import models
from cls import CRUD

activity = CRUD(models.Activity)
logger = logging.getLogger("eAsset.routers.activity")
path = os.path.join(STATIC_ROOT, 'json/activity.json')

async def get_message(key:str, op:str):
    try:
        with open(path) as f:
            data = json.load(f)
        return data[key][op]
    except KeyError:
        raise KeyError(f'could not find message for {key}.{op}')
    except Exception as e:
        logger.critical(f"{e.__class__}: {e}")
    finally:
        f.close()

activity.get_message = get_message