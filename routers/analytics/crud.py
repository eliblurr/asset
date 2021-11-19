from sqlalchemy import func, distinct, Date
from sqlalchemy.orm import Session

async def dates_available(field, model, db:Session):
    dates = db.query(getattr(model, field).cast(Date)).distinct().all()
    return [date[0].year for date in dates]

class Analytics:
    def __init__(self, model):
        self.model = model

    async def sum(self, fields:list, db:Session, group_by=None, order_by=None, **kw):
        sums = [
            func.sum(
                getattr(self.model, field[0])
            ).label(
                field[1]
            ) for field in fields
        ]
        base = db.query(*sums).filter(**kw)
        if group_by:
            attr = getattr(self.model, group_by)
            base = db.query(*sums, attr).filter(**kw).group_by(attr)
        return base.subquery() if subq else base.all()

    async def count(self, db:Session, group_by=None, order_by=None, subq=False, **kw):
        base = db.query(func.count(self.model.id)).filter(**kw)
        if group_by:
            attr = getattr(self.model, group_by)
            base = db.query(func.count(self.model.id), attr).filter(**kw).group_by(attr)
        return base.subquery() if subq else base.all()

    async def min(self, fields:list, db:Session, group_by=None, order_by=None, subq=False, **kw):
        mins = [
            func.min(
                getattr(self.model, field[0])
            ).label(
                field[1]
            ) for field in fields
        ]
        base = db.query(*mins).filter(**kw)
        if group_by:
            attr = getattr(self.model, group_by)
            base = db.query(*mins, attr).filter(**kw).group_by(attr)
        return base.subquery() if subq else base.all()
    
    async def max(self, fields:list, db:Session, group_by=None, order_by=None, subq=False, **kw):
        maxs = [
            func.max(
                getattr(self.model, field[0])
            ).label(
                field[1]
            ) for field in fields
        ]
        base = db.query(*maxs).filter(**kw)
        if group_by:
            attr = getattr(self.model, group_by)
            base = db.query(*maxs, attr).filter(**kw).group_by(attr)
        return base.subquery() if subq else base.all()

    async def avg(self, fields:list, db:Session, group_by=None, order_by=None, subq=False,**kw):
        avgs = [
            func.avg(
                getattr(self.model, field[0])
            ).label(
                field[1]
            ) for field in fields
        ]
        base = db.query(*avgs).filter(**kw)
        if group_by:
            attr = getattr(self.model, group_by)
            base = db.query(*avgs, attr).filter(**kw).group_by(attr)
        return base.subquery() if subq else base.all()

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