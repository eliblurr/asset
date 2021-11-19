from sqlalchemy.orm import Session
from . import models, schemas
from cls import Analytics

asset = Analytics(models.Asset)
request = Analytics(models.Request)
proposal = Analytics(models.Proposal)
inventory = Analytics(models.Inventory)
department = Analytics(models.Department)

async def db_aggregator(keys, years, db:Session):
    pass

async def tenant_aggregator(ids, years, db:Session):
    return {
        "assets":{
            "years": await asset.years_available('created', db)
        },
        "inventories":"",
        "requests":"",
        "proposals":"",
        "departments":"",
    }
    # group by years, monthss
    # pass

# getattr(self.model, field).cast(Date)
# year_filter = filter(models.Asset.created.cast(Date)==year)

# field filters

# Parameter('sort', Parameter.KEYWORD_ONLY, annotation=List[str], default=Query(None, regex=sort_str if sort_str else '(^-)?\w')),])  
# Parameter('fields', Parameter.KEYWORD_ONLY, annotation=List[str], default=Query(None, regex=f'({q_str})$')),
# DT_X = r'^((lt|lte|gt|gte):)?\d\d\d\d-(0?[1-9]|1[0-2])-(0?[1-9]|[12][0-9]|3[01]) (00|[0-9]|1[0-9]|2[0-3]):([0-9]|[0-5][0-9]):([0-9]|[0-5][0-9])?'
# filters.extend([
#     getattr(self.model, k) >= str_to_datetime(val.split(":", 1)[1]) if val.split(":", 1)[0]=='gte'
#     else getattr(self.model, k) <= str_to_datetime(val.split(":", 1)[1]) if val.split(":", 1)[0]=='lte'
#     else getattr(self.model, k) > str_to_datetime(val.split(":", 1)[1]) if val.split(":", 1)[0]=='gt'
#     else getattr(self.model, k) < str_to_datetime(val.split(":", 1)[1]) if val.split(":", 1)[0]=='lt'
#     else getattr(self.model, k) == str_to_datetime(val)
#     for k,v in dte_filters.items() for val in v 
# ])
# getattr(self.model, field).cast(Date)
# sort_str = "|".join([f"{x[0]}|-{x[0]}" for x in self._cols]) if self._cols else None
# q_str = "|".join([x[0] for x in self._cols if x[0]!='password']) if self._cols else None
# if self._cols:
#     params.extend([Parameter(param[0], Parameter.KEYWORD_ONLY, annotation=param[1], default=Query(None)) for param in self._cols if param[1]!=datetime.datetime])
#     params.extend([
#         Parameter(param[0], Parameter.KEYWORD_ONLY, annotation=List[str], default=Query(None, regex=DT_X)) for param in self._cols if param[1]==datetime.datetime
#     ])
# if params['sort']:
#     sort = [f'{item[1:]} desc' if re.search(SORT_STR_X, item) else f'{item} asc' for item in params['sort']]
#     base = base.order_by(text(*sort))


# session.query(Table.column, func.count(Table.column)).group_by(Table.column).all()
# q = session.query(User.id).\
# join(User.addresses).\
# group_by(User.id).\
# having(func.count(Address.id) > 2)

# session.query(func.count(User.id)).\
#         group_by(User.name)

# aggregated_unit_price = Session.query(
#                             func.sum(UnitPrice.price).label('price')
#                         ).group_by(UnitPrice.unit_id).subquery()

# fields is [('column','label')]

# Analytics & Report generation (DB level, Schema(s)/Tenant(s) level, Branch(es) level)
# Aggregations By some factor of some fields (DB level, Schema(s)/Tenant(s) level, Branch(es) level) .eg. group monetary value by currency
#               db
#             /    \
#       tenant      tenant
#        / \         | \
#       /   \        |  \
#      /     \       |   \
#   branch branch branch branch
# 
# ?level=db -> payload:tenants=[some tenant list, *] 
# ?level=tenant -> payload:branches=[some branch list, *]
# min, max, count, avg, sum
# order_by, group_by

# Assets
# - total count
# - total count by status
# - total count by numerable
# - total count by numerable
# - sum of prices by currency
# - total count by consumable
# - total value by consumable
# - total count by year [created]
# - total count by month [created]
# - total count of decomission assets
# - total asset value after depreciation

# Inventory
# - assets groupings in inventory
# - proposal count[grouping by status]
# - count of request[grouping by status]

# Department
# - assets groupings in inventory
# - proposal count[grouping by status]
# - count of request[grouping by status]

# Request
# - total requests
# - request count by status'
# - value of accepted[or other status'] request assets

# Proposal
# - total count by status' 
# - total count of proposals

# Finance
# total value by currency 

# assets = {
#     'years':0,
#     'count':0,
#     'count_by_status':{
#         'decomissioned':0,
#         'numerable':0,
#         'consumable':0
#     },
#     'value':{
#         'GHC':0,
#         'USD':0
#     },
#     'value_by_status':{
#         'decomissioned':0,
#         'numerable':0,
#         'consumable':0
#     },
#     'count_by_years':{
#         '2001':{
#             'count':0,
#             'count_by_status':{
#                 'decomissioned':0,
#                 'numerable':0,
#                 'consumable':0
#             },
#         }
#     },
#     'total':0,
#     'total':0,
#     'total':0,
#     'total':0,
#     'total':0,
#     'total':0,
#     'total':0, 
# }

# if dashboard:
#     return 'dashboard data'
# return 

'''
    if file:
        file_path = os.path.join(path, file)
        if os.path.isfile(file_path):
            if request.url.path=='/logs/download':
                return FileResponse(file_path, media_type='text/plain', filename=f"{file}.log")
            return FileResponse(file_path, media_type='text/plain', stat_result=os.stat(file_path))
        else:
            return "error", {"info":f"File not found"}  
    files_gen_to_list = list(path.iterdir())
    files = [
        {
            "filename": file.name,
            "path": file.as_posix(),
            "entries": get_entries(file)
        }
        for file in files_gen_to_list[offset:offset+limit] if file.is_file()
    ]  
    return {
        "bk_size": files_gen_to_list.__len__(),
        "pg_size": files.__len__(),
        "data": files
    }
'''


# for tenant, for db

# from routers.currency.models import Currency

# from database import SessionLocal

# db = SessionLocal()

# # year = crud.dates_available('created', Currency, db)

# c = crud.Analytics(Currency)
# fields = [('id', 'sum_of_ids'),]
# # values
# r = c.avg( fields, db)
# print(r)

# a = ['*', 'sdf']

# print('*' in a )

'''
c_s = {'visits':VisitView, 'appointments':AppointmentView, 'bills':BillView, 'doctors':ClinicianView, 'chart-examination':ChartExaminationView, 'chart-eye-pressure':ChartEyePressureView, 'chart-refraction':ChartRefractionView, 'patients':PatientView} 

class QPPatientSerializer(PatientSerializer):
    class Meta:
        model = Patient
        fields = ('age', 'is_active' , 'gender', 'is_registered',)
        extra_kwargs = {k:{'required': False, 'allow_null':True} for k in fields}

@api_view(['GET'])
@permission_classes([AllowAny,])
def aggregate(request, model=None):
    start, end, dt_field, m = request.GET.get('start'), request.GET.get('end'), request.GET.get('dt_field'), c_s.get(model, None)
    qp = m.qp_serializer(data=request.query_params, partial=True)
    
    qp.is_valid(raise_exception=True)

    data = qp.data
    data = {k:v for k,v in data.items() if v is not None}

    base = m.model.objects.all().filter(**{f'{k}__exact':v for k,v in data.items()})
    
    if start and end and dt_field:
        start, end = datetime.strptime(start, '%Y-%m-%d'), datetime.strptime(end, '%Y-%m-%d')
        base = base.filter(**{f'{dt_field}__gte':start, f'{dt_field}__lte':end})
    return Response({"total":base.count()})

@api_view(['GET'])
@permission_classes([IsAuthenticated,])
def dashboard(request, model=None):
    user = request.user
    hours = request.GET.get('hours', 24)

    try:
        dt = datetime.datetime.now() - datetime.timedelta(hours = int(hours))
    except:
        return Response({'detail':'hours value to large or is not a valid int'}, status=422)

    patients = {
        'total': Patient.objects.all().count(),
        'registered': Patient.objects.all().filter(is_registered__exact=True).count(),
        'non_registered': Patient.objects.all().filter(is_registered__exact=False).count(),
    }

    appointments = {
        'total': Appointment.objects.all().count(),
        'confirmed': Appointment.objects.all().filter(status__exact='confirmed', date__gte=dt).count(),
        'cancelled': Appointment.objects.all().filter(status__exact='cancelled', date__gte=dt).count(),
        'pending': Appointment.objects.all().filter(status__exact='pending', date__gte=dt).count(),
        'honoured': Appointment.objects.all().filter(status__exact='honoured', date__gte=dt).count(),
        'booked': Appointment.objects.all().filter(status__exact='booked', date__gte=dt).count(),
    }

    screenings = {
        'chart_refraction':{
            'total': ChartRefraction.objects.all().count(),
        },
        'chart_eye_pressure':{
            'total': ChartEyePressure.objects.all().count(),
        },
        'chart_examination':{
            'total': ChartExamination.objects.all().count(),
        }
    }

    visits = {
        'total': Visit.objects.all().count(),
        'screened': Visit.objects.all().filter(status__exact='screened', date__gte=dt, ).count(),
        'examined': Visit.objects.all().filter(status__exact='examined', date__gte=dt).count(),
        'registered': Visit.objects.all().filter(status__exact='registered', date__gte=dt).count(),
    }
    
    if user.role == 'doctor':
        visits.update(
            {   
                'total': Visit.objects.all().filter(id=user.id).count(),
                'screened': Visit.objects.all().filter(status__exact='screened', date__gte=dt, id=user.id).count(),
                'examined': Visit.objects.all().filter(status__exact='examined', date__gte=dt, id=user.id).count(),
                'registered': Visit.objects.all().filter(status__exact='registered', date__gte=dt, id=user.id).count(),
            }
        )
    if user.role == 'screener':
        screenings.update(
            {
                'chart_refraction':{
                    'total': ChartRefraction.objects.all().filter(id=user.id).count(),
                },
                'chart_eye_pressure':{
                    'total': ChartEyePressure.objects.all().filter(id=user.id).count(),
                },
                'chart_examination':{
                    'total': ChartExamination.objects.all().filter(id=user.id).count(),
                }
            }
        )
   
    return Response({'patients':patients, 'appointments':appointments, 'visits':visits, 'screenings':screenings})
'''