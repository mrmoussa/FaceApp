# importing required libraries
from PyQt5 import QtMultimedia
from PyQt5 import QtMultimediaWidgets
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *

import os
import sys
import time

import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import Layer
from confirm import *

import config
# Main window class
class MainWindow(QMainWindow):
    
    
    
    # constructor
    def __init__(self):
        super().__init__()
  
        # setting geometry
        self.setGeometry(100, 100,
                         800, 600)
  
        # setting style sheet
        self.setStyleSheet("background : lightgrey;")
  
        # getting available cameras
        self.available_cameras = QCameraInfo.availableCameras()
  
        # if no camera found
        if not self.available_cameras:
            # exit the code
            sys.exit()
        
         # creating a status bar
        self.status = QStatusBar()
  
        # setting style sheet to the status bar
        self.status.setStyleSheet("background : white;")
  
        # adding status bar to the main window
        self.setStatusBar(self.status)
  
        # path to save
        self.save_path = ""
  
        # creating a QCameraViewfinder object
        self.viewfinder = QCameraViewfinder()
  
        # showing this viewfinder
        self.viewfinder.show()
  
        # making it central widget of main window
        self.setCentralWidget(self.viewfinder)
  
        # Set the default camera.
        self.select_camera(0)
        
        # creating a tool bar
        toolbar = QToolBar("Camera Tool Bar")
  
        # adding tool bar to main window
        self.addToolBar(toolbar)
  
        # creating a photo action to take photo
        click_action = QAction("Capture photo", self)
  
        # adding status tip to the photo action
        click_action.setStatusTip("This will capture picture")
  
        # adding tool tip
        click_action.setToolTip("Capture picture")
  
  
        # adding action to it
        # calling take_photo method
        click_action.triggered.connect(self.click_photo)
  
        # adding this to the tool bar
        toolbar.addAction(click_action)
  
        check_attendance = QAction("Check Attendance", self)
        
        # adding status tip
        check_attendance.setStatusTip("Check your ID")
        
        # adding tool tip
        check_attendance.setToolTip("Check your ID")
        
        # setting calling method to the check attendance action
        # when triggered signal is emitted
        check_attendance.triggered.connect(self.check_attend)
        
        # adding this to the tool bar
        toolbar.addAction(check_attendance)
  
  
        # creating a combo box for selecting camera
        camera_selector = QComboBox()
  
        # adding status tip to it
        camera_selector.setStatusTip("Choose camera to take pictures")
  
        # adding tool tip to it
        camera_selector.setToolTip("Select Camera")
        camera_selector.setToolTipDuration(2500)
        
        # adding items to the combo box
        camera_selector.addItems([camera.description()
                                  for camera in self.available_cameras])
  
        # adding action to the combo box
        # calling the select camera method
        camera_selector.currentIndexChanged.connect(self.select_camera)
  
        # adding this to tool bar
        toolbar.addWidget(camera_selector)
  
        # setting tool bar stylesheet
        toolbar.setStyleSheet("background : white;")
  
  
  
        # setting window title
        self.setWindowTitle("Attendance checking camera")
  
        # showing the main window
        self.show()
        
    # method to select camera
    def select_camera(self, i):
  
        # getting the selected camera
        self.camera = QCamera(self.available_cameras[i])
  
        # setting view finder to the camera
        self.camera.setViewfinder(self.viewfinder)
  
        # setting capture mode to the camera
        self.camera.setCaptureMode(QCamera.CaptureStillImage)
  
        # if any error occur show the alert
        self.camera.error.connect(lambda: self.alert(self.camera.errorString()))
  
        # start the camera
        self.camera.start()
  
        # creating a QCameraImageCapture object
        self.capture = QCameraImageCapture(self.camera)
        
        # showing alert if error occur
        self.capture.error.connect(lambda error_msg, error,
                                   msg: self.alert(msg))
  
        # when image captured showing message
        self.capture.imageCaptured.connect(lambda d,
                                           i: self.status.showMessage("Image captured : " 
                                                                      + str(self.save_seq)))
  
        # getting current camera name
        self.current_camera_name = self.available_cameras[i].description()
  
        # initial save sequence
        self.save_seq = 0
        
     # method to take photo
    def click_photo(self):
  
        # capture the image and save it on the save path
        self.capture.capture(os.path.join("C:\\Users\\Azamat Musaev\\Desktop\\FaceApp_3.0\\application_data\\input_image\\input_image.jpg" % (
            #self.save_seq,
        )))
  
        # increment the sequence
        self.save_seq += 1
        
        #start model func call
        start_model()
        
        
    
        
    # # change folder method
    # def change_folder(self):
  
    #     # open the dialog to select path
    #     path = QFileDialog.getExistingDirectory(self, 
    #                                             "Picture Location", "")
  
    #     # if path is selected
    #     if path:
  
    #         # update the path
    #         self.save_path = path
  
    #         # update the sequence
    #         self.save_seq = 0
    
    
    # check attendance method
    def check_attend(self):
        self.window = QtWidgets.QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.window)
        self.window.show()
    
    # method for alerts
    def alert(self, msg):
  
        # error message
        error = QErrorMessage(self)
  
        # setting text to the error message
        error.showMessage(msg)
        
       
def preprocess(file_path):
    # Read in image from file path
    byte_img = tf.io.read_file(file_path)
    # Load in the image
    img = tf.io.decode_jpeg(byte_img)
    # Preprocessing steps - resizing the image to be 100x100x3
    img = tf.image.resize(img, (100, 100))
     # Scale image to be between 0 and 1 
    img = img/255
    # Return image
    return img         
       
 
# Siamese L1 Distance class
class L1Dist(Layer):
    
    # Init method - inheritance
    def __init__(self, **kwargs):
        super().__init__()
       
    # Magic happens here - similarity calculation
    def call(self, input_embedding, validation_embedding):
        return tf.math.abs(input_embedding - validation_embedding)
          

def verify(model, detection_threshold, verification_threshold):
    # Build results array
    results = []
    verified_image = ''
    localMax = 0
    for image in os.listdir(os.path.join('application_data', 'verification_images')):
        if (image.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif'))):
            input_img = preprocess(os.path.join('application_data', 'input_image', 'input_image.jpg'))
            validation_img = preprocess(os.path.join('application_data', 'verification_images', image))
        
            # Make Predictions 
            result = model.predict(list(np.expand_dims([input_img, validation_img], axis=1)))
            # plt.imshow(input_img)
            
            print(image)
            print(result)
            if result>=detection_threshold and result>localMax:
                verified_image = image
                localMax=result
            results.append(result)

    
    # Detection Threshold: Metric above which a prediciton is considered positive 
    detection = np.sum(np.array(results) > detection_threshold)
    
    # Verification Threshold: Proportion of positive predictions / total positive samples 
    verification = detection / len(os.listdir(os.path.join('application_data', 'verification_images'))) 
    verified = verification > verification_threshold
    
    return results, verified, verified_image


def start_model():
    L1Dist
    # # Reload model 
    global verified_image_name
    siamese_model = tf.keras.models.load_model('siamesemodelv2-good.h5', 
                                    custom_objects={'L1Dist':L1Dist, 'BinaryCrossentropy':tf.losses.BinaryCrossentropy})
    
    results, verified, verified_image_name = verify(siamese_model, 0.5, 0.10)
    print(verified)
    print('----------------------------------------------------------------------------------------------')
    if verified==True and verified_image_name != '':
            print(verified_image_name.split('.')[0])
    else:
        print ('Student Not found')
    config.verified_status = verified_image_name.split('.')[0]
    print("Function called")
    
        
# Driver code
if __name__ == "__main__" :
    
  # create pyqt5 app
  App = QApplication(sys.argv)
  
  # create the instance of our Window
  window = MainWindow()
  
  # start the app
  sys.exit(App.exec())
  