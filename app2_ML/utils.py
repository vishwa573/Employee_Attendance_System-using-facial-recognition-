import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import numpy as np
import tensorflow as tf
from django.conf import settings

def predict_image(captured_images):
    
    captured_images=np.vstack(captured_images)
    model_path=os.path.join(settings.MEDIA_ROOT,'cnn_face_recogniser.keras')
    model=tf.keras.models.load_model(model_path)
    predictions=model.predict(captured_images)
    predicted_labels=np.argmax(predictions, axis=1)#since we use multiple images predictions will be 2D arra
    unique,count = np.unique(predicted_labels,return_counts=True)
    predicted_id=unique[np.argmax(count)]

    confidence = np.max(predictions)
    avg_confidence=np.mean(confidence)

    print('Average Confidence of Prediction: ',avg_confidence,'ID:',predicted_id)
    return predicted_id if avg_confidence>0.965 else None #threshold=0.95 adjust based on callibration