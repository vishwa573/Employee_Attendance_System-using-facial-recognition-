from django.db import models

# Create your models here.
class Employee(models.Model):

    idd=models.AutoField(primary_key=True)
    name=models.CharField(max_length=30)
    email=models.EmailField(unique=True)
    password=models.CharField(max_length=200)
    approved=models.IntegerField(default=0)
    last_login = models.DateTimeField(auto_now=True)
    is_manager=models.IntegerField(default=0)
    image = models.ImageField(upload_to='employee_images/', null=True, blank=True,default=None)
    update_face=models.IntegerField(default=0)#to keep track on how many times a employee has updated a face
    update_face_req=models.IntegerField(default=0)#0-neutral,1-want to update,2-rejected

    def __str__(self):#Where the employee instances are converted to string ,the name will be displayed
        return self.name
    
class Location(models.Model):

    employee=models.ForeignKey(Employee,on_delete=models.CASCADE,related_name='locations')
    name=models.CharField(max_length=30,default='Default Name')
    loc_name=models.CharField(max_length=50,default='No-Name')
    latitude=models.FloatField()
    longtitude=models.FloatField()
    access=models.IntegerField(default=0)#0 means request in action,1 means confirmed,2 -rejected,3 - common location
    time = models.DateTimeField(auto_now=True)

    def save(self,*args,**kwargs):
        if self.name == 'Default Name':
            self.name=self.employee.name
        super(Location, self).save(*args, **kwargs)

    def __str__(self):
        return self.name