import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model # type: ignore
from tensorflow.keras.layers import Dense, Flatten, Input # type: ignore
from django.core.management.base import BaseCommand
from django.conf import settings
from app2_ML.models import Employee



class Command(BaseCommand):
    help='Training the model'
    def handle(self,*args,**kwargs):
        ds_path=os.path.join(settings.MEDIA_ROOT,'employee_images')
        model_path=os.path.join(settings.MEDIA_ROOT,'cnn_face_recogniser.keras')

        encoding=[]
        labels=[]
        employees=Employee.objects.all()
        
        emp_id_as_index={employee.idd : idx for idx,employee in enumerate(employees) }

        for employee in employees:
            
            img_folder=os.path.join(ds_path,str(employee.idd))

            if not os.path.isdir(img_folder):#or use isdir
                continue

            for image in os.listdir(img_folder):# loading data to tf pipeline

                img_path=os.path.join(img_folder,image)
                img = tf.keras.preprocessing.image.load_img(img_path,color_mode='grayscale')
                img=tf.keras.preprocessing.image.img_to_array(img)
                img=img/255
                img=np.expand_dims(img,axis=-1)#for channel(here it is gray)
                img=np.expand_dims(img,axis=0)#for batches we will create
                encoding.append(img)

                labels.append(emp_id_as_index[employee.idd])

        if encoding:
            encodings=np.vstack(encoding)#cause Models expect the input to be as 4D(1,128,128,1)
            labels=np.array(labels)
            #CNN Model,Functional API
            input_shape = (128, 128, 1)
            inputs = Input(shape=input_shape)
            x = tf.keras.layers.Conv2D(32, (3, 3), activation='relu')(inputs)
            x = tf.keras.layers.MaxPooling2D((2, 2))(x)
            x = tf.keras.layers.Conv2D(64, (3, 3), activation='relu')(x)
            x = tf.keras.layers.MaxPooling2D((2, 2))(x)
            x = tf.keras.layers.Conv2D(128, (3, 3), activation='relu')(x)
            x = tf.keras.layers.Flatten()(x)
            x = tf.keras.layers.Dense(256, activation='relu')(x)    
            predictions = tf.keras.layers.Dense(len(emp_id_as_index), activation='softmax')(x)
            model = Model(inputs=inputs, outputs=predictions)
            model.compile(optimizer='adam',loss='sparse_categorical_crossentropy',metrics=['accuracy'])


            # Use early stopping to prevent overfitting
            early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
            model.fit(encodings,labels,epochs=20,batch_size=32,validation_split=0.2,callbacks=[early_stopping])
            model.save(model_path)

            self.stdout.write(self.style.SUCCESS(f'Model training completed and saved to {model_path}'))
        else:
            self.stdout.write(self.style.ERROR('No face encodings found.'))

