Camera and lighting drift monitor


Purpose:

To check the consistancy of the image paramters over a period of time using the saved images.
Inconsistencies in image acquisition causes degradation in the system performance over time.
Inconsistencies may occur over a period of time because of use along with wear and tear.


Problem Statement:

To compare image parameter like Sharpness, Brightness and Shift in features.

Sharpness helps to identify if the camera is focused correctly.
Brightness helps to identify the consistant intensity of the light source used.
Shift helps in identifying if the mounting is secure.


Technologies used:

Python, OpenCV, NumPy, Matplotlib, FPDF2


How to Install and run:

pip install -r requirements.txt
python main_v2.py


Output:

The program calculates the image parameters using the referance image along with the ROI identified by the user.
CSV file of all the calculated values are stored in the root folder.
PDF report is generated with all the calculated values and a grapical representation of the values.
Secifications for Sharpness and Brightness can be modified as per the user requirements.