import numpy as np
from keras.models import model_from_json
import operator
import cv2
import sys, os

#=================================================================================================================================================================================================================
# Loading the model
json_file = open("CNNMODEL.json", "r")
model_json = json_file.read()
json_file.close()
loaded_model = model_from_json(model_json)

#---------------------------------------------------------------------------------------------------
# load weights into new model
loaded_model.load_weights("CNNMODEL.h5")
print("Model is loaded from disk")

cap = cv2.VideoCapture(0)

#=================================================================================================================================================================================================================
# Category dictionary
categories = {0: 'Victory', 1: 'Thumb', 2: 'Fist', 3: 'Palm'}
directory = 'Output images'
myList = os.listdir(directory)
overlayList = []
for imPath in myList:
    image = cv2.imread(f'{directory}/{imPath}')
    img = cv2.resize(image, (200, 200))
    overlayList.append(img)

while True:
    _, frame = cap.read()
    kernel = np.ones((1,1),np.uint8)
    #---------------------------------------------------------------------------------------------------
    # Simulating mirror image
    frame = cv2.flip(frame, 1)

    #---------------------------------------------------------------------------------------------------
    # Coordinates of the ROI
    x1 = int(0.5*frame.shape[1])
    y1 = 10
    x2 = frame.shape[1]-10
    y2 = int(0.5*frame.shape[1])
    # Drawing the ROI
    # The increment/decrement by 1 is to compensate for the bounding box
    cv2.rectangle(frame, (x1-1, y1-1), (x2+1, y2+1), (255,0,0) ,1)
    # Extracting the ROI
    roi = frame[y1:y2, x1:x2]

    #---------------------------------------------------------------------------------------------------
    # Resizing the ROI so it can be fed to the model for prediction
    roi = cv2.resize(roi, (64, 64)) 
    roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    _, test_image = cv2.threshold(roi, 170, 255, cv2.THRESH_BINARY)
    test_image = cv2.morphologyEx(test_image, cv2.MORPH_OPEN, kernel)
    cv2.imshow("test", test_image )
    # Batch of 1
    result = loaded_model.predict(test_image.reshape(1, 64, 64, 1))
    prediction = {'Victory': result[0][0], 
                  'Thumb': result[0][1], 
                  'Fist': result[0][2],
                  'Palm': result[0][3],}
    
    #---------------------------------------------------------------------------------------------------
    # Sorting based on top prediction
    prediction = sorted(prediction.items(), key=operator.itemgetter(1), reverse=True)

    #---------------------------------------------------------------------------------------------------
    if(prediction[0][0]=="Victory"):
        frame[0:200, 0:200] = overlayList[0]
    elif(prediction[0][0]=="Thumb"):
        frame[0:200, 0:200] = overlayList[1]
    elif(prediction[0][0]=="Fist"):
        frame[0:200, 0:200] = overlayList[2]
    elif(prediction[0][0]=="Palm"):
        frame[0:200, 0:200] = overlayList[3]
        
    # Displaying the predictions
    cv2.putText(frame, prediction[0][0], (50, 230), cv2.FONT_HERSHEY_PLAIN, 1.5, (0,0,255), 2)
    cv2.imshow("Frame", frame)
    
    interrupt = cv2.waitKey(10)
    if interrupt & 0xFF == 27: # esc key
        break
        
cap.release()
cv2.destroyAllWindows()
