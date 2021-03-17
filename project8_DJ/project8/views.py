from django.shortcuts import render, redirect
from django.db.models import Count
from .models import Teacher, DataSet, DataSource
from project8.resources import DataResource
import os
from tablib import Dataset
from datetime import datetime
import time
from django.contrib.auth.decorators import login_required
# Pages 
@login_required(login_url='admin/login')
def index(request):
    posts   = Teacher.objects.all().values('speciality').annotate(total=Count('speciality')).order_by('total')
    gender  = Teacher.objects.all().values('gender').annotate(total=Count('degree')).order_by('total')
    degree = Teacher.objects.all().values('degree').annotate(total=Count('address')).order_by('total')
    # dataset  = Teacher.objects.all().values('dataset').annotate(total=Count('dataset')).order_by('total')
    address  = Teacher.objects.all().values('address').annotate(total=Count('address')).order_by('total')
    context = {
        'data': posts,
        'gender': gender,
        'degree': degree,
        'source': address,
    }
    return render(request, 'pages/index.html', context)

@login_required(login_url = 'admin/login')
def invoice(request):
    return render(request, 'pages/invoice.html')


@login_required(login_url = 'admin/login')
def projects(request):
    return render(request,'pages/projects.html')

@login_required(login_url='admin/login')
def tables(request):
    if request.method == 'POST':
        subject_name=request.POST['subject']
        teachers = Teacher.objects.raw(f"SELECT * FROM project8_teacher WHERE subject = '{subject_name}' LIMIT 20")
        drop = Teacher.objects.values('subject').distinct()
    else:
        teachers = Teacher.objects.all()[:10]
        drop = Teacher.objects.values('subject').distinct()
    return render(request,"pages/tables.html", {'teachers':teachers, "drop":drop})
def testdata(request):
    posts = Teacher.objects.all().values('speciality').annotate(total=Count('speciality')).order_by('total')
    context = {
        'data': posts,
    }
    return render(request, 'project8/index.html', context)
#End  Pages 
## upload data sets
@login_required(login_url='admin/login')
def import_data(request):
    error = ''
    datasource = DataSource.objects.all()

    if request.method == 'POST' and request.FILES['file'].name.split('.')[1].lower() in ['xlsx', 'csv']:
        file = request.FILES['file']
        option = request.POST['option']
        start_time = time.time()
        dataset_obj1 = DataSet()
        dataset_obj1.date = datetime.today().strftime('%Y-%m-%d')
        dataset_obj1.file_name = file.name
        dataset_obj1.execution_time = start_time
        dataset_obj1.num_of_records = 0
        dataset_obj1.source_id = option
        dataset_obj1.save()
        last_id = DataSet.objects.last()
        if request.FILES['file'].name.split('.')[1] == 'xlsx':
            resource_teacher = DataResource()
            dataset = Dataset()
            file = request.FILES['file']
            imported_data = dataset.load(file.read(), format='xlsx')
            record_num = 0
            for col in imported_data:
                if col[1] is None:
                    dataset_obj2 = DataSet.objects.get(id=last_id.id)
                    dataset_obj2.execution_time = round((time.time() - start_time), 4)
                    dataset_obj2.num_of_records = record_num
                    dataset_obj2.save()
                    return redirect('/tables')
                value = Teacher(
                    col[0],
                    col[1],
                    col[2],
                    col[3],
                    col[4],
                    col[5],
                    col[6],
                    col[7],
                    col[8],
                    col[9],
                    last_id.id
                )
                value.save()
                record_num += 1
        elif request.FILES['file'].name.split('.')[1] == 'csv':
            resource_teacher = DataResource()
            dataset = Dataset()
            file = request.FILES['file']
            imported_data = dataset.load(file.read().decode(), format='csv')
            record_num = 0
            for col in imported_data:
                value = Teacher(
                    col[0],
                    col[1],
                    col[2],
                    col[3],
                    col[4],
                    col[5],
                    col[6],
                    col[7],
                    col[8],
                    col[9],
                    last_id.id
                )
                record_num += 1
                value.save()
            dataset_obj2 = DataSet.objects.get(id=last_id.id)
            dataset_obj2.execution_time = round((time.time() - start_time), 4)
            dataset_obj2.num_of_records = record_num
            dataset_obj2.save()
            return redirect('/tables')
        else:
            error = 'Invalid input, Pleases make sure to put either CSV or XLSX'

    return render(request, 'pages/form_upload.html', {'datasource': datasource, 'error': error})

# Create your views here.