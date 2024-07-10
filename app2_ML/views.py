from django.shortcuts import redirect, render
from django.contrib import messages
from .models import Employee

import cv2
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import numpy as np
from django.conf import settings
import tensorflow as tf
import time
from app1.utils import update_attendance
from .utils import predict_image

# Create your views here.
def capture_image(request, employee_id):
    
    if not request.session.get('employee_id'):
        messages.error(request,'Signin to Access the Page')
        return redirect("signin")

    employee = Employee.objects.get(idd=employee_id)

    
    emp_dir=os.path.join(settings.MEDIA_ROOT,'employee_images',f'{employee_id}')#create a folder for each employee id
    if not os.path.exists(emp_dir):
        os.makedirs(emp_dir)
    
    if request.method == 'POST':
        cap = cv2.VideoCapture(0)   
        if not cap.isOpened():
            print("camera not opened")
            messages.error(request,'Unable to open Camera')
            if employee.is_manager==1:
                return render(request,'app1/index.html',{'username':employee.name,'id':employee_id,'registered':1,'manager':1})
            return render(request,'app2_ML/recognise_face.html',{'username':employee.name,'id':employee_id})
        captured_images=[]
        check_images=[]
        max_length=15
        image_count=0

        while image_count<max_length:
            ret, frame = cap.read()
            if not ret:
                print(1)
                messages.error(request,'Failed to capture image')
                if employee.is_manager==1:
                    return render(request,'app1/index.html',{'username':employee.name,'id':employee_id,'registered':1,'manager':1})
                return render(request,'app2_ML/recognise_face.html',{'username':employee.name,'id':employee_id})
        
            text = f'Turn your face for each image'
            cv2.putText(frame, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            text = f'Image {image_count }/{max_length}'
            cv2.putText(frame, text, (50, 75), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            cv2.imshow('Capture Image', frame)
            key = cv2.waitKey(1)
            if key == ord('c'):
                # Preprocess
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
                face = face_classifier.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40))
                if len(face)>0:
                    (top,right,bottom,left) = face[0]
                    face_img = gray[right:right+left,top:top+bottom]
                    resized_img=cv2.resize(face_img,(128,128))# for our deep learning model to have same sized images
                    captured_images.append(resized_img)
                    print("image_count",image_count)
                    image_count+=1# only write this line after detected face
                    resized_img=resized_img/255
                    resized_img=np.expand_dims(resized_img,axis=0)
                    resized_img=np.expand_dims(resized_img,axis=-1)
                    check_images.append(resized_img)#For checking if the face already exist

            elif key == ord('q'):
                cap.release()
                cv2.destroyAllWindows()
                messages.error(request,'The process has been halted')
                if employee.is_manager==1:
                    return render(request,'app1/index.html',{'username':employee.name,'id':employee_id,'manager':1})
                return render(request,'app1/index.html',{'username':employee.name,'id':employee_id})
                

        # Release the camera and close the OpenCV windows
        cap.release()
        cv2.destroyAllWindows()

        predicted_id=predict_image(check_images[0:5])
        
        if predicted_id != None:#We can directly return to the main page ,but to find the match running this code below
            print("Predicted_id:",predicted_id) 
            registered_emp=Employee.objects.filter(image__isnull = False)

            employees=Employee.objects.all()
            emp_id_as_index={emp.idd : idx for idx,emp in enumerate(employees)}

            for emp in registered_emp:
                print("Employee with registerd face:",emp.idd)
                if emp_id_as_index[emp.idd] == predicted_id:
                    print("MAtched id:",emp.idd)
                    messages.error(request,'This Face has already been registered.Contact admin for queries')
                    if employee.is_manager==1:
                        return render(request,'app1/index.html',{'username':employee.name,'id':employee_id,'manager':1})
                    return render(request,'app1/index.html',{'username':employee.name,'id':employee_id})
                

        if image_count==max_length:
            for i,img in enumerate(captured_images):
                img_path=os.path.join(settings.MEDIA_ROOT,'employee_images',f'{employee_id}',f'{employee_id}_{i}.png')
                cv2.imwrite(img_path,img)

                if(i==0):
                    employee.image=img_path     #store the first image in DB
                    employee.save()
            
            messages.success(request,'Registered Face')
            if employee.is_manager==1:
                return render(request,'app1/index.html',{'username':employee.name,'id':employee_id,'registered':1,'manager':1})

            return render(request,'app1/index.html',{'username':employee.name,'id':employee_id,'registered':1})
        
        messages.error(request,"Failed to capture image in the process")
        
    return render(request, 'app2_ML/capture.html', {'employee': employee})


def recognise(request, employee_id):
    if not request.session.get('employee_id'):
        messages.error(request,'Signin to Access the Page')
        return redirect("signin")
    employee=Employee.objects.get(idd=employee_id)

    if request.method == 'POST':
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():  
            messages.error(request,'Unable to open Camera')
            if employee.is_manager==1:
                return render(request,'app1/index.html',{'username':employee.name,'id':employee_id,'registered':1,'manager':1})
            return render(request,'app2_ML/recognise_face.html',{'username':employee.name,'id':employee_id,'registered':1})
        
        captured_images=[]
        max_length=5
        img_count=0
        c=0
        

        while img_count<max_length:
            
            #print(img_count)
            ret, frame = cap.read()
            if not ret:
                messages.error(request,"Failed to capture image")
                if employee.is_manager==1:
                    return render(request,'app1/index.html',{'username':employee.name,'id':employee_id,'registered':1,'manager':1})
                return render(request,'app2_ML/recognise_face.html',{'username':employee.name,'id':employee_id,'registered':1})
            
            cv2.imshow('Recognise Face',frame) 
            key = cv2.waitKey(1) if c == 0 else ord('c')
            if key == ord('c'): 
                c+=1
                print (c)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
                face = face_classifier.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40))
                if len(face)>0:
                    (top,right,bottom,left) = face[0]
                    face_img = gray[right:right+left,top:top+bottom]
                    resized_img=cv2.resize(face_img,(128,128))# for our deep learning model to have same sized images
                    resized_img=resized_img/255
                    resized_img=np.expand_dims(resized_img,axis=0)
                    resized_img=np.expand_dims(resized_img,axis=-1)
                    captured_images.append(resized_img)
                    img_count+=1# only write this line after detected face
                        
                else:
                    messages.error(request,"No face detected")
                    cap.release()
                    cv2.destroyAllWindows()
            elif key == ord('q'):
                cap.release()
                cv2.destroyAllWindows()
                messages.error(request,'The process has been halted')
                if employee.is_manager==1:
                    return render(request,'app1/index.html',{'username':employee.name,'id':employee_id,'manager':1})
                return render(request,'app1/index.html',{'username':employee.name,'id':employee_id})
            
        cap.release()
        cv2.destroyAllWindows()

        if captured_images:

            predicted_id=predict_image(captured_images)
            print("Predicted ID:",predicted_id)

            employees=Employee.objects.all()
            emp_id_as_index={emp.idd : idx for idx,emp in enumerate(employees)}

            if predicted_id == emp_id_as_index[employee_id]:
                x=update_attendance(employee_id)
                if x == 2:
                    messages.success(request,'Already Marked attendance for the day')
                if x == 1:
                    messages.success(request,"Attendance Marked")
                if employee.is_manager==1:
                    return render(request,'app1/index.html',{'username':employee.name,'id':employee_id,'registered':1,'manager':1})
                return render(request,'app1/index.html',{'username':employee.name,'id':employee.idd,'registered':1})
            
            else:
                messages.error(request,"Face mismatch!,contact admin for queries")
                if employee.is_manager==1:
                    return render(request,'app1/index.html',{'username':employee.name,'id':employee_id,'registered':1,'manager':1})
                return render(request,'app1/index.html',{'username':employee.name,'id':employee.idd,'registered':1})
    
    return render(request,'app2_ML/recognise_face.html',{'employee_id':employee_id})

def update_image(request,employee_id):

    if not request.session.get('employee_id'):
        messages.error(request,'Signin to Access the Page')
        return redirect("signin")
    employee=Employee.objects.get(idd=employee_id)

    emp=Employee.objects.get(idd=employee_id)
    if emp.update_face_req==0 or emp.update_face_req==1:
        emp.update_face_req=1
        emp.save()
        messages.error(request,'Your request has been sent to the manager.Please wait for his approval')

        if employee.is_manager==1:
            return render(request,'app1/index.html',{'username':employee.name,'id':employee_id,'registered':1,'manager':1})
        
        return render(request,'app1/index.html',{'username':emp.name,'id':emp.idd,'registered':1})
    elif emp.update_face_req==2:
        emp.update_face_req=0
        emp.save()
        messages.error(request,'Your request has been rejected by the manager.The requset has been submitted again')

        if employee.is_manager==1:
            return render(request,'app1/index.html',{'username':employee.name,'id':employee_id,'registered':1,'manager':1})
        return render(request,'app1/index.html',{'username':emp.name,'id':emp.idd,'registered':1})

    elif emp.update_face_req == 3:
        if request.method== 'POST':
            try:
                image_count=0
                captured_images=[]
                c=0
                folder_path=os.path.join(settings.MEDIA_ROOT,'employee_images',str(employee_id))
                cap=cv2.VideoCapture(0)
                if not cap.isOpened():  
                    messages.error(request,'Unable to open Camera')
                    if employee.is_manager==1:
                        return render(request,'app1/index.html',{'username':employee.name,'id':employee_id,'registered':1,'manager':1})
                    return render(request,'app1/index.html',{'username':employee.name,'id':employee.idd,'registered':1})


                while image_count<5:
                    ret,frame=cap.read(0)
                    if not ret:
                        messages.error(request,"Failed to capture image")
                        if employee.is_manager==1:
                            return render(request,'app1/index.html',{'username':employee.name,'id':employee_id,'registered':1,'manager':1})
                        return render(request,'app1/index.html',{'username':employee.name,'id':employee.idd,'registered':1})

                    cv2.imshow('Update_image',frame)
                    key=cv2.waitKey(1)

                    if key == ord('c') if c==0 else ord('c') :
                        c+=1
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
                        face = face_classifier.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40))

                        if len(face)>0:
                            (top,right,bottom,left) = face[0]
                            face_img = gray[right:right+left,top:top+bottom]
                            resized_img=cv2.resize(face_img,(128,128))# for our deep learning model to have same sized images
                            captured_images.append(resized_img)
                            print("image_count",image_count)
                            image_count+=1# only write this line after detected face

                        else:
                            messages.error(request,"No face detected")
                            cap.release()
                            cv2.destroyAllWindows()
                    elif key == ord('q'):
                        cap.release()
                        cv2.destroyAllWindows()
                        messages.error(request,'The process has been halted')
                        if employee.is_manager==1:
                            return render(request,'app1/index.html',{'username':employee.name,'id':employee_id,'manager':1})
                        return render(request,'app1/index.html',{'username':employee.name,'id':employee_id})
                    
                cap.release()
                cv2.destroyAllWindows()

                employee=Employee.objects.get(idd=employee_id)
                if captured_images:
                    for idx,img in enumerate(captured_images):
                        img_path=os.path.join(folder_path,f'{employee_id}_upd{employee.update_face}_{idx}.png')
                        cv2.imwrite(img_path,img)

                    employee.update_face+=1
                    employee.update_face_req=0
                    employee.save()
                    messages.success(request,"Updated_image")
                else:
                    messages.error(request,'Error during Capturing image')
                if employee.is_manager==1:
                    return render(request,'app1/index.html',{'username':employee.name,'id':employee_id,'registered':1,'manager':1})
                return render(request,'app1/index.html',{'username':employee.name,'id':employee.idd,'registered':1})

            except Exception as e:
                print('Error:',e)
                messages.error(request,e)

    return render(request,'app2_ML/update_img.html',{'employee_id':employee_id})