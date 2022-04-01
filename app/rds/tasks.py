from services.broadcaster import send_message
from services.aws import s3_upload, s3_delete
from services.webpush import send_web_push
from config import settings, UPLOAD_ROOT
from services.sms import send_sms
from services.email import email
from utils import delete_path, logger
from .queues import get_queue
import os, shutil, re
from rq import Retry

def report_success(job, connection, result, *args, **kwargs):
    print('success')

def report_failure(job, connection, type, value, traceback):
    print('failed', traceback.print_exc())

max_retry = settings.REDIS_MAX_RETRIES
intervals =[n*settings.REDIS_RETRY_INTERVAL for n in range(max_retry)]

params = {
    'retry':Retry(max=max_retry, interval=intervals),
    'on_success':report_success,
    'on_failure':report_failure
}

def async_send_email(*args, **kwargs):
    q = get_queue('email')
    if q:return q.enqueue(email,*args, **kwargs, **params)    

def async_s3_upload(*args, **kwargs):
    q = get_queue('file')
    if q:return q.enqueue(s3_upload,*args, **kwargs, **params)    

def async_s3_delete(*args, **kwargs):
    q = get_queue('file')
    if q:return q.enqueue(s3_delete,*args, **kwargs, **params)    

def async_send_sms(*args, **kwargs):
    q = get_queue('sms')
    if q:return q.enqueue( send_sms,*args, **kwargs, **params )  
  
def async_delete_path(*args, **kwargs):
    q = get_queue('file')
    if q:return q.enqueue(delete_path,*args, **kwargs, **params)  

def async_remove_file(url):
    if isinstance(url, str):
        if re.search(r'(s3.amazonaws.com)', url):
            async_s3_delete(url.split('s3.amazonaws.com/')[1]) 
        else:
            async_delete_path(f'{UPLOAD_ROOT}{url.split("/media")[1]}')

def async_send_web_push(*args, **kwargs):
    q = get_queue('notification')
    if q:return q.enqueue(send_web_push,*args, **kwargs, **params)  

def async_send_message(*args, **kwargs):
    q = get_queue('broadcaster')
    if q:return q.enqueue(send_message, *args, **kwargs, **params)  

def async_logger(*args, **kwargs):
    q = get_queue('file')
    if q:return q.enqueue(logger, *args, **kwargs, **params)  