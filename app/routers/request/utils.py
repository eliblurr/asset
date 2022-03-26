from rds.tasks import async_send_email, async_send_message, async_send_web_push
from datetime import timedelta, datetime
from scheduler import scheduler
from utils import gen_code

notify = lambda push_id, message : async_send_message(channel=push_id, message=message)
web_push = lambda subscription_info, message : async_send_web_push(subscription_info=subscription_info, message_body=message) 
terminate_reminders = lambda id : [scheduler.remove_job(job.id) for job in scheduler.get_jobs() if job.split('_',1)[0]==str(id)]
terminate_reminder = lambda id, name : [scheduler.remove_job(job.id) for job in scheduler.get_jobs() if job.split('_',1)[0]==str(id) and job.name==name]
send_mail = lambda kwargs : async_send_email(mail=Mail(**kwargs)) # subject=subject, recipients=recipients, body=body, template_name=template_name
email_reminder = lambda id, date, name, kwargs : scheduler.add_job(send_mail, kwargs=kwargs, id=f'{id}_ID{gen_code(10)}', trigger='date', run_date=date, name=name) #kwargs = recipients, subject, body, template_name

def emit_action(target, op, *args, **kwargs):

    op_switcher = lambda op: { 
        'expired':{
            'func':(terminate_reminders, send_mail),
            'params':[
                (target.id,), 
                ({
                    'request_code':target.code, 
                    'subject':f'Expired Request',
                    'template_name':'request.html',
                    'recipients':[target.author.email],
                    'body':{
                        'title':target.asset_rq.asset.title if target.asset_rq else target.consumable_rq.consumable.title, 
                        f'{"asset" if target.asset_rq else "consumable"}_code':target.asset_rq.asset.code if target.asset_rq else target.consumable_rq.consumable.code, 
                    },
                    'status':'EXPIRED'
                },)
            ]
        },
        'declined':{
            'func':(terminate_reminders, send_mail),
            'params':[
                (target.id,), 
                ({
                    'request_code':target.code, 
                    'subject':f'Declined Request',
                    'template_name':'request.html',
                    'recipients':[target.author.email],
                    'body':{
                        'title':target.asset_rq.asset.title if target.asset_rq else target.consumable_rq.consumable.title, 
                        f'{"asset" if target.asset_rq else "consumable"}_code':target.asset_rq.asset.code if target.asset_rq else target.consumable_rq.consumable.code, 
                    },
                    'status':'DECLINED'
                },)
            ]
        },
        'accepted':{
            'func':(notify, terminate_reminder, terminate_reminder, send_mail),
            'params':[
                (target.author.push_id, {
                    'key':'request', 
                    'id':target.id,
                    'title':target.asset_rq.asset.title if target.asset_rq else target.consumable_rq.consumable.title, 
                    f'{"asset" if target.asset_rq else "consumable"}_code':target.asset_rq.asset.code if target.asset_rq else target.consumable_rq.consumable.code,
                    f'{"asset" if target.asset_rq else "consumable"}_id':target.asset_rq.asset.id if target.asset_rq else target.consumable_rq.consumable.id,
                }),
                (target.id, 'send-mail-reminder'), 
                (target.id, 'expire-request'), 
                ({
                    'request_code':target.code, 
                    'subject':f'Accepted Request',
                    'template_name':'request.html',
                    'recipients':[target.author.email],
                    'body':{
                        'title':target.asset_rq.asset.title if target.asset_rq else target.consumable_rq.consumable.title, 
                        f'{"asset" if target.asset_rq else "consumable"}_code':target.asset_rq.asset.code if target.asset_rq else target.consumable_rq.consumable.code, 
                    },
                    'status':'ACCEPTED'
                },)
            ]
        },
        'returned':{
            'func':(terminate_reminders),
            'params':[(target.id,)]
        },
        'picked':{
            'func':(terminate_reminder, email_reminder if target.asset_rq.return_deadline else None),
            'params':[
                (target.id, 'send-mail-reminder-pickup_deadline'),
                ({
                    'request_code':target.code, 
                    'subject':f'Asset return reminder',
                    'template_name':'request.html',
                    'recipients':[target.author.email],
                    'body':{
                        'title':target.asset_rq.asset.title, 
                        f'asset_code':target.asset_rq.asset.code
                    },
                    'status':'PICKED'
                }),
            ]
        },
        'ready':{
            'func':(send_mail, terminate_reminder, reminder if target.asset_rq else None ),
            'params':[
                ({
                    'request_code':target.code, 
                    'subject':f'Requested item is ready',
                    'template_name':'request.html',
                    'recipients':[target.author.email],
                    'body':{
                        'title':target.asset_rq.asset.title if target.asset_rq else target.consumable_rq.consumable.title, 
                        f'{"asset" if target.asset_rq else "consumable"}_code':target.asset_rq.asset.code if target.asset_rq else target.consumable_rq.consumable.code, 
                    },
                    'status':'READY'
                }),
                (target.id, 'name'),

                (
                    target.id, 
                    target.asset_rq.pickup_deadline-timedelta(hours=8) if target.asset_rq.pickup_deadline else datetime.now()-timedelta(hours=1),
                    'send-mail-reminder-pickup_deadline', 
                    {
                        'request_code':target.code, 
                        'subject':'Item Pickup reminder',
                        'template_name':'request.html',
                        'recipients':[target.author.email],
                        'body':{
                            'title':target.asset_rq.asset.title, 
                            'asset_code':target.asset_rq.asset.code 
                        },
                        'status':'READY'
                    }
                ),
            ]
        },
    }

    if op=='bk_notify': # for only assets, no consumables
        send_mail({
            'request_code':target.code, 'subject':f'Declined Request',
            'template_name':'request.html', 'recipients':kwargs.get('email_list', []),
            'body':{ 'title':target.asset_rq.asset.title, 'code':target.asset_rq.asset.code, },
            'status':'Declined'
        })

    elif op=='notify':
        notify(target.author.push_id, message=kwargs.get('message'))

    elif op=='schedule-job':
        pass

    else:
        func, params = op_switcher.get(op).get('func', None), op_switcher.get(op).get('params', None)
        if func and params:
            for func in func:
                func(*params[i])
                i+=1
