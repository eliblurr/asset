from rds.tasks import async_send_email, async_send_message, async_send_web_push
from datetime import timedelta, datetime
from scheduler import scheduler
from config import STATIC_ROOT
from utils import gen_code
import os, json

def messages():
    with open(os.path.join(STATIC_ROOT, 'json/messages.json')) as file:
        messages = json.load(file)  
        file.close()
    return messages

notify = lambda push_id, message : async_send_message(channel=push_id, message=message)
web_push = lambda subscription_info, message : async_send_web_push(subscription_info=subscription_info, message_body=message) 
terminate_reminders = lambda id : [scheduler.remove_job(job.id) for job in scheduler.get_jobs() if job.split('_',1)[0]==str(id)]
terminate_reminder = lambda id, name : [scheduler.remove_job(job.id) for job in scheduler.get_jobs() if job.split('_',1)[0]==str(id) and job.name==name]
send_mail = lambda kwargs : async_send_email(mail=Mail(**kwargs)) # subject=subject, recipients=recipients, body=body, template_name=template_name
email_reminder = lambda id, date, name, kwargs : scheduler.add_job(send_mail, kwargs=kwargs, id=f'{id}_ID{gen_code(10)}', trigger='date', run_date=date, name=name) #kwargs = recipients, subject, body, template_name
notify_reminder = lambda id, date, name, push_id, message : scheduler.add_job(send_mail, kwargs={'push_id':push_id, 'message':message}, id=f'{id}_ID{gen_code(10)}', trigger='date', run_date=date, name=name)

def emit_action(request, obj, op, *args, **kwargs):

    op_switcher = lambda op: { 
        'expired':{
            'func':(terminate_reminders, send_mail),
            'params':[
                (request.id,), 
                ({
                    'request_code':request.code, 
                    'subject':f'Expired Request',
                    'template_name':'request.html',
                    'recipients':[request.author.email],
                    'body':{
                        'title':obj.title, 
                        'type':request.tag,
                        'code':obj.code 
                    },
                    'status':'EXPIRED'
                },)
            ]
        },
        'declined':{
            'func':(terminate_reminders, send_mail),
            'params':[
                (request.id,), 
                ({
                    'request_code':request.code, 
                    'subject':f'Declined Request',
                    'template_name':'request.html',
                    'recipients':[request.author.email],
                    'body':{
                        'title':obj.title, 
                        'type':request.tag,
                        'code':obj.code 
                    },
                    'status':'DECLINED'
                },)
            ]
        },
        'returned':{
            'func':(terminate_reminders),
            'params':[(request.id,)]
        },
    }

    if op=='bk_notify': # for only assets, no consumables
        status = kwargs.get('status')
        send_mail({
            'request_code':request.code, 
            'subject':f'{status} Request',
            'template_name':'request.html', 
            'recipients':kwargs.get('email_list', []),
            'body':{'title':obj.title, 'code':obj.code},
            'status':status
        })

    elif op=='notify':
        notify(request.author.push_id, message=kwargs.get('message'))

    elif op=='schedule-email-job':
        obj = obj.asset if request.asset_rq else obj.consumable
        email_reminder(
            id=request.id,
            name = kwargs.get('name'), #'smr-pickup-deadline'/'smr-return-deadline'
            date = kwargs.get('date'),
            kwargs = {
                'request_code':request.code, 
                'subject':f'Expired Request',
                'template_name':'request.html',
                'recipients':[request.author.email],
                'body':{
                    'title':obj.title, 
                    'type':request.tag,
                    'code':obj.code 
                },
            })

    elif op=='picked':
        terminate_reminder(request.id, 'smr-pickup-deadline')
        if request.asset_rq:
            if obj.return_deadline:
                email_reminder(
                    id=request.id,
                    name = 'smr-return-deadline',
                    date = obj.return_deadline,
                    kwargs={
                        'request_code':request.code, 
                        'subject':f'Asset return reminder',
                        'template_name':'request.html',
                        'recipients':[request.author.email],
                        'body':{
                            'title':obj.title, 
                            'code':obj.code 
                        },
                    }
                )

    elif op=='ready':
        send_mail(
            kwargs={
                'request_code':request.code, 
                'subject':f'Asset is ready for pick up',
                'template_name':'request.html',
                'recipients':[request.author.email],
                'body':{
                    'title':obj.title, 
                    'code':obj.code 
                },
            }
        ),
        if request.asset_rq:
            if obj.pickup_deadline:
                email_reminder(
                    id=request.id,
                    name = 'smr-pickup-deadline',
                    date = obj.pickup_deadline,
                    kwargs={
                        'request_code':request.code, 
                        'subject':f'Asset pick up reminder',
                        'template_name':'request.html',
                        'recipients':[request.author.email],
                        'body':{
                            'title':obj.title, 
                            'code':obj.code 
                        },
                    }
                )

    elif op=='accepted':
        terminate_reminder(request.id, 'expire-request')
        terminate_reminder(request.id, 'expiry-notify-reminder')
        send_mail(
            kwargs={
                'request_code':request.code, 
                'subject':f'Asset request has been accepted',
                'template_name':'request.html',
                'recipients':[request.author.email],
                'body':{
                    'title':obj.title, 
                    'code':obj.code 
                },
            }
        )

        notify(
            obj.asset.inventory.manager.push_id if request.asset_rq else obj.consumable.inventory.manager.push_id, 
            message={
                'key':'request',
                'message': messages['request']['accepted'],
                'meta': {
                    'id':request.id, 
                    'type':request.tag, 
                    'request_code':request.code, 
                    'title':obj.title, 'id':obj.id, 
                    'author_id':request.author.id, 
                    'author':f'{request.author.full_name()}'
                }
            }
        )

    else:
        func, params = op_switcher.get(op).get('func', None), op_switcher.get(op).get('params', None)
        if func and params:
            for func in func:
                func(*params[i])
                i+=1