
# Package Detector

## Description
This is a project made using Python, OpenCV and various other libraries. It can use either a webcam or smartphone camera to detect packages by using colour detection, estimate its dimensions and its (x,y,z) coordinates relative to the camera and also reads its barcode when placed close enough.



## Demo

![](https://github.com/tashad19/package-detector/blob/main/working1.gif)



## Usage

### Installation instructions
- Python 3.x with pip
- Requirements.txt: For downloading other packages, open cmd and run:
``` python
pip install -r requirements.txt
```

### Camera options
For testing purpose, you can use either:
- Smartphone Camera: Run the ColourDetectionWebcam.py file using this command:
``` python
python ColourDetectionWebcam.py
```
- Webcam: Run the ColourDetectionCam.py file using this commands:
``` python
python ColourDetectionCam.py
```

### Steps for using smartphone camera:
1. Install 'IP Webcam' app from play store on your phone
2. Choose the 'Start server' option
3. Note the IPv4 address displayed on bottom. Keep the camera running.
4. Go to the ColourDetectionWebcam.py file, go to 'PASTE YOUR IPv4 HERE' and modify the value of url variable for only the ip address. Leave the other things as it is.
5. Run this python file

![](https://github.com/tashad19/package-detector/blob/main/IP%20camera%20steps.jpg)

### Explanation of windows 
After running either of the two programs, you will see 3 windows pop up:
1. Object Detection: It displays the mask of the frame. HSV values are preset by me but you can adjust them to match the colour of package.
2. Object with metrics: It is the actual window in which all the measurements and bounding box are displayed for the frame.
3. Reference Image: This is the 'reference.jpg' image you provided in the same directory with the marker. It is used for finding the focal length using similar triangles method.

### Reference image
For the program to run, you have to provide a reference image with the name 'reference.jpg' in the same working directory. 
This is used for finding focal length for distance(z) and size estimations.


## Features

- (x,y,z) coordinates: Look for x,y,z variables in the while True loop
- Length and width of bounding box: Look for dimA, dimB in the while True loop
- Barcode reading: myData variable in the barcode loop


## Optimizations



