import numpy as np
import cv2
import sys
import scipy.ndimage as scindi
from glob import glob
from skimage.filters import threshold_adaptive
from tqdm import tqdm

def isSmearDetected(src):
    data=glob(src+"/*.jpg")
    print('No of files are :- ' + str(len(data)))
    file_name_suffix = src.split('/')[len(src.split('/'))-1]
    meanByPixel = cv2.imread("Mean_" + file_name_suffix +".jpg")
    total_data_len = len(data)
    if meanByPixel is None:
    # if resizedRead is None:
        print(f'Mean Image was not found, filename :- ' + 'Mask_' + file_name_suffix +'.jpg')
        # total_data_len = len(data)

        # find mean of all pixel values of all images
        meanByPixel = np.zeros((500,500,3),np.float)
        progressBar = 0
        lastProg = 0
        for img in data:
            curr_image = cv2.imread(img)
            # resize all images to the same size i.e. 500x500
            resize_curr_image = cv2.resize(curr_image,(500,500))
            #resize_curr_image = cv2.medianBlur(resize_curr_image,5)
            i = np.array(resize_curr_image,dtype=np.float)
            meanByPixel += i

            # progress bar that updates at every 10%
            progress = ((progressBar) * 100) / total_data_len
            if progress >= lastProg:
                print ("Progress: "+str(progress) + "%")
                lastProg +=10
            progressBar += 1
            #     tqdm(progress)
            #     lastProg += 10
            # progressBar += 1

        meanByPixel = meanByPixel /total_data_len
                # write mean image to the disk.
        cv2.imwrite("Mean_" + file_name_suffix +".jpg", meanByPixel)
        # cv2.imshow("Average Image", meanByPixel)
    else:
        print(f'Mean Image was found filename :- ' + 'Mean_' + file_name_suffix +'.jpg')

    meanByPixel = np.array(np.round(meanByPixel),dtype=np.uint8)

    # convert mean image to grayscale means BGR -- > GRAY ( 3 pixel value to 1D pixel value )
    grayMeanImage = cv2.cvtColor(meanByPixel, cv2.COLOR_BGR2GRAY)

    # find ThresholdImage by using adaptiveThreshold method
    thresholdImage = cv2.adaptiveThreshold(grayMeanImage,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY, 105, 11)
    cv2.imshow("Adaptive threshold and Gaussian Img", thresholdImage)
    cv2.waitKey()
    cv2.imwrite("Adaptive threshold and Gaussian Img" + file_name_suffix + ".jpg", thresholdImage)

    # edge detection
    mask = cv2.Canny(thresholdImage, 200, 200)
    cv2.imshow("Mask",mask)
    cv2.waitKey()
    # cv2.imwrite("MaskImg.jpg",mask)

    # find invert image which will act as mask
    #mask = cv2.bitwise_not(thresholdImage)

    # save mask to the disk
    cv2.imwrite("Mask_" + file_name_suffix +".jpg",mask)

    # read random image from the directory to detect the smear
    read = data[0]
    readImage = cv2.imread(read)
    resizedRead = cv2.resize(readImage,(500,500))
    cv2.imshow('Original Image', resizedRead)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


    # # find contours on mask image
    # contours,_ = cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    #
    # if contours:
    #     # if contours is size of smear then locate it on our randomly piced image
    #     # draw contours around smear on original image
    #     result = cv2.drawContours(resizedRead,contours,-1,(0,255,255),2)
    #
    #     # save the image to the disk.
    #     cv2.imwrite("final_"+src.split('/')[1]+".jpg",resizedRead)
    #     cv2.imshow("Final Result",result)
    #     cv2.waitKey(0)
    #     cv2.destroyAllWindows()
    #     return True
    # return False

    # find contours on mask image
    contours,_ = cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # if contours is size of smear then locate it on our randomly piced image
        # draw contours around smear on original image
        result = cv2.drawContours(resizedRead,contours,-1,(0,255,255),2)

        # save the image to the disk.
        # cv2.imwrite("final_"+ file_name_suffix +".jpg",resizedRead)
        cv2.imshow("Final Result",result)
        cv2.imwrite("Final Result" + file_name_suffix +".jpg", result)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return True
    return False

if __name__ == "__main__":
     #To check the path of image directory
    if len(sys.argv) < 2:
        print("Please provide path to the image folder")
        sys.exit(1)
    print("Processing images from the path provided for smear detection")
    if(isSmearDetected(sys.argv[1])):
        print ("Smear is detected for source.")
    else:
        print("No Smear in ")
