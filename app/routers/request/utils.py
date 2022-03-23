from rds.tasks import async_send_email, async_send_message, async_send_web_push
from services.broadcaster import Publish
from scheduler import scheduler
from utils import gen_code

notify = lambda id, message : async_send_message(Publish(channel=id, message=message)) # channel is user_id
web_push = lambda subscription_info, message : async_send_web_push(subscription_info=subscription_info, message_body=message) 
terminate_reminders = lambda id : [scheduler.remove_job(job.id) for job in scheduler.get_jobs() if job.split('_',1)[0]==str(id)]
terminate_reminder = lambda id, name : [scheduler.remove_job(job.id) for job in scheduler.get_jobs() if job.split('_',1)[0]==str(id) and job.name==name]
send_mail = lambda recipients, subject, body, template_name : async_send_email(mail=Mail(subject=subject, recipients=recipients, body=body, template_name=template_name))
email_reminder = lambda id, date, name, recipients, subject, body, template_name : scheduler.add_job(send_mail, kwargs={'recipients':recipients, 'body':body, 'subject':subject, 'template_name':template_name}, id=f'{id}_ID{gen_code(10)}', trigger='date', run_date=date, name=name)

op_switcher = lambda target: { 
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
        'func':(notify, send_mail, terminate_reminder, terminate_reminder),
        'params':[
            ([req.author.id], 'some message'),
            ([req.author.email],  'subject', {'body':1}, 'template_name', ),
            (req.id, 'name'), 
            (req.id, 'name')
        ]
    },
    'returned':{
        'func':(terminate_reminders),
        'params':[(req.id,)]
    },
    'picked':{
        'func':(terminate_reminder, email_reminder if req.return_deadline else None),
        'params':[
            (req.id, 'name'),
            (id, 'date', 'name', [req.author.email], 'subject', {'body':1}, 'template_name')
        ]
    },
    'ready':{
        'func':(send_mail, reminder, terminate_reminder),
        'params':[
            ([req.author.email], 'inactive-request', {'asset_name':obj.title}, 'template_name' ),
            (id, 'date', 'name', [req.author.email], 'subject', {'body':1}, 'template_name'),
            (req.id, 'name'),
        ]
    },
}

def emit_action(target, op, *args, **kwargs):
    print(target, op)
    if op=='bk_notify':
        pass
        return
    if op=='notify':
        pass
        return
    if op=='schedule-job':
        pass
        return
    if op in ['schedule-job', 'notify', 'bk_notify']:
        return
    
    func, params = op_switcher.get(op).get('func', None), op_switcher.get(op).get('params', None)
    if func and params:
        for func in func:
            func(*params[i])
            i+=1
