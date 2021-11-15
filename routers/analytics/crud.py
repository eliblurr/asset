# Analytics & Report generation (DB level, Schema(s)/Tenant(s) level, Branch(es) level)
# Aggregations By some factor of some fields (DB level, Schema(s)/Tenant(s) level, Branch(es) level) .eg. group monetary value by currency

'''
c_s = {'visits':VisitView, 'appointments':AppointmentView, 'bills':BillView, 'doctors':ClinicianView, 'chart-examination':ChartExaminationView, 'chart-eye-pressure':ChartEyePressureView, 'chart-refraction':ChartRefractionView, 'patients':PatientView} 

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