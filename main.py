#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import torch

from models.modelB4 import LDC

from preprocessing.img_processing import transform, pixel_adjust
from preprocessing.save_images import save_image_to_disk

device = torch.device('cpu' if torch.cuda.device_count() == 0 else 'cuda')
 
#Loading Model
model = LDC().to(device)


# Pretrained Weights Path
checkpoint_path = 'weights/BRIND/11/11_model.pth'

def predict_img(checkpoint_path, file_path, save_path='output/average'):
    
    #Extract the Filename
    file_names =[file_path.split('/')[-1]] 
    
    #Read Original Image 
    img = cv2.imread(file_path)
  
    print(img.shape)    
    #Tensor Conversion of Shape for Pre-processing & Scaling of Image
    image_shape = [torch.tensor([img.shape[0]]), torch.tensor([img.shape[1]])]
    
    #Loading Model weights & Eval Call
    model.load_state_dict(torch.load(checkpoint_path,map_location=device))
    model.eval()
    
    #Transorm Image (Channel First format) based on Prediction Model
    images, mean_rgb = transform(img)
    
    
    # Prediction Block
    try:
        preds = model(images)
        print('Prediction Successfull')
    except Exception as e:
        # Handling of Pixel adjustment
        print('Error:', e)
        img = pixel_adjust(img)
        print('Adjusting Pixel')
        images, mean_rgb = transform(img)
        preds = model(images)
        
    
    #Save Image as well as return output image array
    output = save_image_to_disk(preds, file_names, save_path, image_shape)
    
    return output, img
    

