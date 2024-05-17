import cv2
import numpy as np
import torch

# mean_bgr = [103.939,116.779,123.68,137.86][0:3]
def transform(img):
    
    mean_bgr = cv2.mean(img)[0:3]


    # Calculate the mean pixel values
    img_width = img.shape[1]
    img_height = img.shape[0]
    
    test_img_width = img.shape[1]

    test_img_height = img.shape[0]
    
    test_data = "CLASSIC"
    # gt[gt< 51] = 0 # test without gt discrimination
    if test_data == "CLASSIC":
        img_height = img_height
        img_width = img_width
        print(
            f"actual size: {img.shape}, target size: {(img_height, img_width,)}")
        # img = cv2.resize(img, (img_width, img_height))
        img = cv2.resize(img, (img_width, img_height))
        gt = None

    # Make images and labels at least 512 by 512
    elif img.shape[0] < 512 or img.shape[1] < 512:
        img = cv2.resize(img, (test_img_width, test_img_height))  # 512
        gt = cv2.resize(gt, (test_img_width, test_img_height))  # 512

    # Make sure images and labels are divisible by 2^4=16
    elif img.shape[0] % 16 != 0 or img.shape[1] % 16 != 0:
        img_width = ((img.shape[1] // 16) + 1) * 16
        img_height = ((img.shape[0] // 16) + 1) * 16
        img = cv2.resize(img, (img_width, img_height))
        gt = cv2.resize(gt, (img_width, img_height))
    else:
        img_width = test_img_width
        img_height = test_img_height
        img = cv2.resize(img, (img_width, img_height))
        gt = cv2.resize(gt, (img_width, img_height))
    # # For FPS
    # img = cv2.resize(img, (496,320))
    # if yita is not None:
    #     gt[gt >= yita] = 1
    img = np.array(img, dtype=np.float32)
    
    img = img[:, :, ::-1]  # RGB->BGR
    img -= mean_bgr
    img = img.transpose((2, 0, 1))
    img = torch.from_numpy(img.copy()).float()

    if test_data == "CLASSIC":
        gt = np.zeros((img.shape[:2]))
        gt = torch.from_numpy(np.array([gt])).float()
    else:
        gt = np.array(gt, dtype=np.float32)
        if len(gt.shape) == 3:
            gt = gt[:, :, 0]
        gt /= 255.
        gt = torch.from_numpy(np.array([gt])).float()
    
    img =img.unsqueeze(0)
    print('Transform successful')

    return img, mean_bgr


def resize(img, percentage=10):
        
    # Get the original image dimensions
    height, width = img.shape[:2]
    
    # Calculate the new dimensions
    new_height = int(height * (100-percentage)/100)
    new_width = int(width * (100-percentage)/100)
    
    # Resize the image
    resized_img = cv2.resize(img, (new_width, new_height))
    
    return resized_img

def pixel_adjust(img):
    # Get the original image dimensions
    height, width = img.shape[:2]
    
    # Add a black border of 1 pixel to the left and right sides of the image
    border_size = 1 # Pixel for Widthd
    bordered_img = cv2.copyMakeBorder(img, 0, 0, border_size, border_size, cv2.BORDER_CONSTANT, value=[255, 255, 255])
    
    return bordered_img


