from routers.consumable.models import Consumable
from exceptions import NotFound, BadRequestError
from routers.catalogue.models import Catalogue
from routers.priority.models import Priority
from routers.user.account.models import User
from sqlalchemy.orm import Session
from database import SessionLocal
from scheduler import scheduler
from . import models, schemas
from cls import CRUD

request = CRUD(models.Request)

async def validate_author(id, db:Session):
    obj = db.query(User).filter_by(id=id).first()
    if not obj:raise NotFound(f'user with id:{id} not found')
    if obj.department:
        return obj.department.head_of_department, {"department_id":obj.department.id} 
    return None, {}

async def validate_priority(id, db:Session):
    obj = db.query(Priority).filter_by(id=id).first()
    if not obj:raise NotFound(f'priority with id:{id} not found')
    return True

async def validate_asset(id:int, db:Session):
    obj = db.query(models.Asset).filter_by(id=id).first()
    if not obj:raise NotFound(f'asset with id:{id} not found')
    if not obj.available:raise BadRequestError(f'asset with id:{id} not available')
    return obj.inventory.department.head_of_department if obj.inventory.department else obj.inventory.manager, {'title':obj.title, 'code':obj.code, 'id':id, 'type':'assets'}, {"inventory_id":obj.inventory.id}

async def validate_consumable(id, quantity, db:Session):
    obj = db.query(Consumable).filter_by(id=id).first()
    if not obj:raise NotFound(f'consumable with id:{id} not found')
    obj.validate_quantity(quantity, db)
    return obj.inventory.department.head_of_department if obj.inventory.department else obj.inventory.manager, {'title':obj.title, 'quantity':obj.quantity, 'id':id, 'type':'consumables'}, {"inventory_id":obj.inventory.id}

def remove_scheduled_jobs(id:int):
    map(scheduler.remove_job, [job.id for job in scheduler.get_jobs() if job.split('_',1)[0]==str(id)])

def expire(id:int, email:str, asset_name:str, db=SessionLocal()):
    request = db.query(models.Request).filter_by(id=id).first()
    if request: 
        request.status=schemas.RequestStatus.expired
        db.commit()
        
    # notify here -> send_async_email.delay(mail=Mail(email=[email], content={'asset_name':asset_name}).json(), template=email('inactive-request')) 
    # try:     
    #     async_send_email(mail={
    #         "subject":"Account Activation", "recipients":[tenant.email],
    #         "body":f"your password reset link is: {urljoin(request.base_url, settings.VERIFICATION_PATH)}?token={token}" 
    #     })
    # except Exception as e:logger(__name__, e, 'critical')

    remove_scheduled_jobs(id)

async def transfer(*args, **kwargs):
    pass

async def update_request(id:int, payload:schemas.UpdateRequest, db:Session):
    req = await request.read_by_id(id, db)
    if not req:
        raise NotFound(f'request with id:{id} not found')

#     notify = lambda data, id : emit_event('private-message', {'message':{'data':data}, 'client_id':id})
#     terminate_reminders = lambda id : [scheduler.remove_job(job.id) for job in scheduler.get_jobs() if job.split('_',1)[0]==str(id)]
#     send_mail = lambda emails, content, template_key : send_async_email.delay(mail=Mail(email=emails, content=content).json(), template=email(template_key))
#     terminate_reminder = lambda id, name : [scheduler.remove_job(job.id) for job in scheduler.get_jobs() if job.split('_',1)[0]==str(id) and job.name==name]
#     reminder = lambda date, name, emails, content, template_key : scheduler.add_job(send_mail, kwargs={'emails':emails, 'content':content, 'template_key':template_key}, id=f'{id}_ID{gen_code(10)}', trigger='date', run_date=date, name=name)

#     # cancel all active requests for the same item
#     if payload.action==schemas.Action.accepted:
#         db.query(models.Request).filter(
#             and_(
#                 models.Request.id != id,
#                 models.Request.item_id == req.item_id,
#                 models.Request.status == schemas.RequestStatus.active
#             )
#         ).update({'status': schemas.RequestStatus.inactive, 'action':schemas.Action.declined})
#         req.item.available = False

#     # request can only be ready when accepted
#     if payload.action==schemas.Action.ready and req.action.value!='accepted':
#         raise HTTPException(status_code=400, detail='request has not been accepted')
    
#     # set request inventory when request is accepted
#     if payload.action==schemas.Action.accepted:
#         req.inventory_id = req.item.inventory_id

#     # make item available when request is declined or returned
#     if payload.action==schemas.Action.declined or payload.action==schemas.Action.returned or payload.action==schemas.Action.completed:
#         req.item.available = True

#     req_u = await request.update(id, payload, db)

#     if req and req_u: 
#         data = {'id':req.id, 'title':req.item.title, 'code':req.item.code, 'item_id':req.item_id}
#         status_switcher = {
#             schemas.RequestStatus.expired:{
#                 'func':(terminate_reminders, send_mail),
#                 'params':(
#                     (req_u.id,),
#                     ([req_u.author.email], {'asset_name':req_u.item.title}, 'inactive-request')
#                 )
#             },
#             schemas.RequestStatus.inactive:{
#                 'func':(terminate_reminders, send_mail),
#                 'params':(
#                     (req_u.id,),
#                     ([req_u.author.email], {'asset_name':req_u.item.title}, 'inactive-request')
#                 )
#             }
#         }

#         action_switcher = {
#             schemas.Action.ready: {
#                 'func':(send_mail, reminder),
#                 'params':(
#                     ([req_u.author.email], {'asset_name':req_u.item.title, 'deadline':req_u.pickup_deadline}, 'asset-ready-reminder'),
#                     (req_u.pickup_deadline-timedelta(hours=8) if req_u.pickup_deadline else datetime.now()-timedelta(hours=8), 'send-mail-reminder-pickup_deadline', [req_u.author.email], {'asset_name':req_u.item.title, 'pickup_deadline':req_u.pickup_deadline}, 'asset-ready-reminder')
#                 )
#             },
#             schemas.Action.picked: {
#                 'func':(terminate_reminder, reminder if req_u.return_deadline else None), 
#                 'params':(
#                     (req_u.id, 'send-mail-reminder-pickup_deadline'),
#                     (req_u.return_deadline-timedelta(hours=8) if req_u.return_deadline else datetime.now()-timedelta(hours=8), 'send-email-reminder-return-deadline', [req_u.author.email], {'asset_name':req_u.item.title, 'return_date':req_u.return_deadline}, 'return-asset') if req_u.return_deadline else None,
#                 )
#             },
#             schemas.Action.returned: {
#                 'func':(terminate_reminders),
#                 'params':(
#                     (req_u.id,)
#                 )
#             },
#             schemas.Action.accepted: {
#                 'func':(notify, send_mail, terminate_reminder, terminate_reminder),
#                 'params':(
#                     ({'key':'request', 'id':req.id, 'title':req.item.title, 'code':req.item.code, 'item_id':req.item_id}, req_u.inventory.manager_id), 
#                     ([req_u.author.email], {'asset_name':req_u.item.title,'justification':payload.justification or ''}, 'accepted-request'),
#                     (req_u.id, 'send-mail-reminder'),
#                     (req_u.id, 'expire-request'),
#                 )
#             },
#             schemas.Action.declined: {
#                 'func':(terminate_reminders, send_mail),
#                 'params':(
#                     (req_u.id,),
#                     ([req_u.author.email], {'asset_name':req_u.item.title, 'justification':payload.justification or ''}, 'declined-request')
#                 )
#             },
#             schemas.Action.completed: {
#                 'func':(terminate_reminders),
#                 'params':(
#                     (req_u.id,)
#                 )
#             }
#         }

#         if req_u.action!=req.action:
#             func, params = action_switcher.get(req_u.action).get('func'), action_switcher.get(req_u.action).get('params')
#             for func in func:
#                 func(*params[i])
#                 i+=1

#         if req_u.status!=req.status:
#             func, params = status_switcher.get(req_u.status).get('func'), status_switcher.get(req_u.status).get('params')
#             for func in func:
#                 func(*params[i])
#                 i+=1
#     return req_u
    

'''
target for request [manager]
author department manager
asset inventory department manager
asset inventory manager
'''
