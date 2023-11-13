from keras.models import load_model
from PIL import Image, ImageOps #Install pillow instead of PIL
import numpy as np
import os 
# Disable scientific notation for clarity
np.set_printoptions(suppress=True)


class AI_model():
    
    def __init__(self,model,class_name):
        # Load the model
        self.model = load_model(model, compile=False)
        # Load the labels
        self.class_names = open(class_name, 'r').readlines()
        
    def predict(self,img_file):
    
        image=self.get_input_image(img_file)

        data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
        #turn the image into a numpy array
        image_array = np.asarray(image)

        # Normalize the image
        normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1

        # Load the image into the array
        data[0] = normalized_image_array

        # run the inference
        prediction = self.model.predict(data)
        index = np.argmax(prediction)
        class_name = self.class_names[index]
        print(self.class_names)
        confidence_score = prediction[0][index]
        
        return confidence_score,class_name
    
    def get_input_image(self,img_file):

        image = Image.open(img_file).convert('RGB')
        size = (224, 224)
        image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)    
        return image    
     


if __name__ == '__main__':  

    model_dir='model'
    model_file='keras_Model.h5'
    label_file='labels.txt'
    upload_img='下載.png'
    
  
    model_file=os.path.join(model_dir,model_file)
    class_file=os.path.join(model_dir,label_file)
    model=AI_model(model_file,class_file)
    
    img_file=os.path.join('upload',upload_img)
    conf,label=model.predict(img_file)
    
    print('Class:', label, end='')
    print('Confidence score:', conf)
 
