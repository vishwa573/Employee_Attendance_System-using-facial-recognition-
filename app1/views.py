from django.shortcuts import redirect, render
from django.contrib import messages
from .models import Employee,Location
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.utils.timezone import now
from django.contrib.auth.hashers import make_password,check_password
from django.conf import settings
from .utils import calculate_distance,download_attendance,get_attendance
import pandas as pd
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


def display(request):
    return render (request, 'app1/index.html')


def displayy(request,manager_id,manager_name):
    if not request.session.get('employee_id'):
        messages.error(request,'Signin to Access the Page')
        return redirect("signin")

    return render(request,'app1/index.html',{'username':manager_name,'id':manager_id,'manager':1})

def validate_password(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        strength = "Very Weak"
        score = 0

        if len(password) >= 8:
            score += 1
        if any(char.islower() for char in password):
            score += 1
        if any(char.isupper() for char in password):
            score += 1
        if any(char.isdigit() for char in password):
            score += 1
        if any(not char.isalnum() for char in password):
            score += 1

        if score == 5:
            strength = "Very Good"
        elif score == 4:
            strength = "Good"
        elif score == 3:
            strength = "OK"
        elif score == 2:
            strength = "Weak"
        elif score == 1:
            strength = "Very Weak"

        return JsonResponse({"strength": strength})

    return HttpResponseBadRequest('Invalid request method.')

def signin(request):

    
    if request.method == "POST":
        idd=request.POST['idd']
        password1=request.POST['password']
        lat=float(request.POST['lat'])#str to float
        long=float(request.POST['long'])
        print('Lat:',lat,'Long:',long)
        
        try:
            try:
                validate_email(idd)
                email=idd
                employee=Employee.objects.get(email=email)

            except ValidationError :
                try:
                    idd=int(idd)
                    employee=Employee.objects.get(idd=idd)
                except ValueError:
                    messages.error(request,"Invalid Credentials")
                    return redirect('signin')
            
            
            if check_password(password1,employee.password):
                if employee.is_manager==1:
                    
                    #logger.debug(f"Logging in as manager: {employee}")
                    request.session['employee_id'] = employee.idd
                    request.session['employee_name'] = employee.name
                    request.session['is_manager'] = 1
                    messages.success(request,'Signed in Successfully')
                    return render(request,'app1/index.html',{'username':employee.name,'id':employee.idd,'manager':1})#call manager_view
                
                if employee.approved==1:

                    Allow=calculate_distance(employee.idd,lat,long)
                    if Allow == True :
                        #logger.debug(f"Logging in as employee: {employee}")
                        request.session['employee_id'] = employee.idd
                        request.session['employee_name'] = employee.name
                        messages.success(request,'Signed in Successfully')

                        if employee.image:
                            return render(request,'app1/index.html',{'username':employee.name,'id':employee.idd,'registered':1})
                        else:
                            return render(request,'app1/index.html',{'username':employee.name,'id':employee.idd})
                        
                    else :

                        #messages.error(request, 'You are not within the Allowed Locations.The request for signing-in in this location has been sent to the manager  ')
                        return redirect('loc_name',employee_id=employee.idd,lat=lat,long=long)
                        
                if employee.approved==0:
                    messages.error(request,'Your registerastion is still not confirmed by the admin  ')

                if employee.approved==2:
                    messages.error(request,'Your registeration request has been declined by admin,Please contact Administration for queries  ')
            else:
                messages.error(request,"Password is incorrect  ")
            
        except Employee.DoesNotExist:
            messages.error(request,'Invalid Id or email  ')
            return render(request,'app1/signin.html')
    return render (request, 'app1/signin.html')

def loc_name(request,employee_id,lat,long):
    
    if request.method=='POST':
        name=request.POST['location_name']
        lat=float(lat)
        long=float(long)
        employee=Employee.objects.get(idd=employee_id)
        emp_loc=Location(employee=employee,latitude=lat,longtitude=long,access=0,loc_name=name)
        emp_loc.save()
        messages.success(request,'Request for this location sent Successfully ')
        return render (request, 'app1/signin.html')
    return render(request,'app1/loc_name.html')
def signout(request):
    
    request.session.flush()
    messages.success(request,"Signed Out Successfully")
    return redirect('display')


def register(request):
    if request.method == "POST":
        name=request.POST['name']
        email=request.POST['email']
        password1=request.POST['password1']
        password2=request.POST['password2']

        if password1!=password2:
            messages.error(request,'Passwords doesnt match')
            return render(request,'app1/register.html')
        
        
        if Employee.objects.filter(email=email).exists():
            messages.error(request,'email already exists')
            return render(request,'app1/register.html')
        
        
        employee = Employee(name=name, email=email, password=make_password(password1))
        employee.last_login=now()
        employee.save()

        '''Lat= 9.921584444757245 #common locations
        Long= 78.14872044418888
        emp_loc=Location(employee=employee,lat=Lat,long=Long,access=3)
        emp_loc.save()'''

        
        messages.success(request,"Account Created Succesfully")
        return redirect('signin')


    return render (request, 'app1/register.html')


def download(request,employee_id):
    if not request.session.get('employee_id'):
        messages.error(request,'Signin to Access the Page')
        return redirect("signin")
    
    employee=Employee.objects.get(idd=employee_id)
    report_type = request.GET.get('report_type')
    if not report_type:
        messages.error(request, 'Please select a report type')
        return render(request, 'app1/index.html', {'username': employee.name, 'id': employee_id, 'registered': 1})
    
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    count=1
    if report_type == 'custom':
        if not start_date or not end_date:
            messages.error(request, 'Please provide both start and end dates for the custom report')
            return render(request, 'app1/index.html', {'username': employee.name, 'id': employee_id, 'registered': 1})
        else:
            count = 5
            emp_attendance = get_attendance(employee_id, count, start_date, end_date)

    if count==1:#Because I am using 2 functions to get emp_attendance,so using count to stop overriding of emp_attendance
        emp_attendance=download_attendance(employee_id,report_type)

    if not emp_attendance:
        messages.error(request,'No attendance Record is found for this employee')
        return render(request,'app1/index.html',{'username':employee.name,'id':employee_id,'registered':1})
    
    df=pd.DataFrame(emp_attendance,columns=['ID','Status','Date','Time'])
    csv_file=df.to_csv(index=False)

    response=HttpResponse(csv_file,content_type='text/csv')
    response['Content-Disposition']=f'attachment; filename=attendace_{employee_id}.csv'
    return response


def manager_view(request,manager_id,manager_name):
    if not request.session.get('employee_id'):
        messages.error(request,'Signin to Access the Page')
        return redirect("signin")
    
    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        btn = request.POST.get('btn')
        if btn == '1':
            Employee.objects.filter(idd=employee_id).update(approved=1)
        elif btn =='2':
            Employee.objects.filter(idd=employee_id).update(approved=2)#reject means 2

    employees = Employee.objects.filter(approved=0)

    context = {'employees': employees,'username':manager_name,'id':manager_id}
    return render(request, 'app1/manager.html', context)

def update_faces(request,manager_id,manager_name):  
    if not request.session.get('employee_id'):
        messages.error(request,'Signin to Access the Page')
        return redirect("signin")    

    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        btn = request.POST.get('btn')
        if btn == '1':
            Employee.objects.filter(idd=employee_id).update(update_face=1)
            Employee.objects.filter(idd=employee_id).update(update_face_req=3)#can update
        elif btn =='2':
            Employee.objects.filter(idd=employee_id).update(update_face_req=2)#2 means rejected

    employees=Employee.objects.all()
    employee=[employee for employee in employees if employee.update_face_req == 1]
    update_req = {'update_req':employee,'username':manager_name,'id':manager_id}

    return render(request,'app1/update_faces.html',update_req)

def approved_registerations(request,manager_id,manager_name):  
    if not request.session.get('employee_id'):
        messages.error(request,'Signin to Access the Page')
        return redirect("signin")

            
    employees=Employee.objects.filter(approved=1)
    approved = {'employees':employees,'username':manager_name,'id':manager_id,'appr':1}
    
    return render(request,'app1/appr_rej.html',approved)

def rejected_registerations(request,manager_id,manager_name):  
    if not request.session.get('employee_id'):
        messages.error(request,'Signin to Access the Page')
        return redirect("signin")

    employees=Employee.objects.filter(approved=2)
    rejected = {'employees':employees,'username':manager_name,'id':manager_id,'rej':1}

    return render(request,'app1/appr_rej.html',rejected)

def update_locations(request,manager_id,manager_name):  
    if not request.session.get('employee_id'):
        messages.error(request,'Signin to Access the Page')
        return redirect("signin")    

    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        location_id = request.POST.get('location_id')
        btn = request.POST.get('btn')
        employee=Employee.objects.get(idd=employee_id)
        if btn == '1':
            Location.objects.filter(id=location_id).update(access=1)#approve
        elif btn =='2':
            Location.objects.filter(id=location_id).update(access=2)#reject

    employees=Employee.objects.filter(locations__access=0).distinct()
    #print(employees)
    context = {'employees': employees,'username':manager_name,'id':manager_id}
    
    return render(request,'app1/update_loc.html',context)   


def see_attendance(request, manager_id, manager_name):
    if not request.session.get('employee_id'):
        messages.error(request, 'Signin to Access the Page')
        return redirect("signin")

    employee_id = request.GET.get('employee_id', None)
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)

    if employee_id:
        if start_date:
            if end_date:
                count = 5
                emp_attendance = get_attendance(employee_id, count, start_date, end_date)
            else:
                count = 4
                emp_attendance = get_attendance(employee_id, count, start_date, start_date)
        else:
            count = 1
            emp_attendance = get_attendance(employee_id, count, '0-0-0', '0-0-0')
    elif start_date:
        if end_date:
            count = 3
            emp_attendance = get_attendance(9872918721, count, start_date, end_date)
        else:
            count = 2
            emp_attendance = get_attendance(9872918721, count, start_date, start_date)
    elif end_date:
        count=6
        emp_attendance = get_attendance(9872918721, count, '0-0-0', end_date)

    else:
        count = 0
        emp_attendance = get_attendance(9872918721, count, '0-0-0', '0-0-0')

    return render(request, 'app1/see_attendance.html', { 'emp_attendance': emp_attendance, 'username': manager_name,'id': manager_id })

def remove_employees(request, manager_id, manager_name):
    if not request.session.get('employee_id'):
        messages.error(request, 'Signin to Access the Page')
        return redirect("signin")
    
    employees = Employee.objects.all()

    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        try:
            employee = Employee.objects.get(idd=employee_id)
            employee.delete()
            messages.success(request, f'Employee {employee.name} has been removed successfully.')
        except Employee.DoesNotExist:
            messages.error(request, 'Employee does not exist.')
        
    employees = Employee.objects.all()
    return render(request, 'app1/remove_employee.html', {'employees': employees, 'username': manager_name, 'id': manager_id})