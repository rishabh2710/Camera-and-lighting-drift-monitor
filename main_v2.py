import os
import cv2
import csv
import numpy as np
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector
from fpdf import FPDF
from fpdf.enums import Align
from PIL import Image

###functions
# Load folder
def choose_folder():
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    folder = filedialog.askdirectory(title="Select folder containing images")
    root.destroy()
    if not folder:
        raise SystemExit("No folder selected. Exiting.")
    return Path(folder)

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}
all_img_path=[]
img_name=[]
# Load train image
def s_train_img(image_paths):
    print("\nImages found:")
    global img_name
    file=[]
    for i in image_paths.iterdir():
        if i.is_file() and i.suffix.lower() in SUPPORTED_EXTENSIONS:
            n=i.name
            file.append(i.name)
            img_name.append(str(n))
        all_img_path.append(str(image_paths)+"\\" +str(i.name))
    print(file)
    while True:
        idx = input("\nEnter the index of training image: ").strip()
        try:
            if  int(idx) <= len(file):
                return str(image_paths)+"/" +file[(int(idx))]
        except ValueError:
            pass
        print(f"Please enter a number from 0 to {len(file)}.")
    

# Display Original Image
def display_orgimg(image,title):
    if image.ndim == 3 and image.shape[2]==3:
        img=cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
    elif image.ndim == 3 and image.shape[2]==4:
        img=cv2.cvtColor(image,cv2.COLOR_BGRA2RGB)
    elif image.ndim==2:
        img=image
    else:
        raise ValueError("Unsupported type")
    fig, ax = plt.subplots(figsize=(12,8))
    ax.imshow (img)
    ax.set_title(title)
    ax.axis("off")
    fig.tight_layout()
    plt.show()

# Display GrayScale Image    
def display_grayimg(image,title):
    fig, ax = plt.subplots(figsize=(12,8))
    ax.imshow (image,cmap="gray")
    ax.set_title(title)
    ax.axis("off")
    fig.tight_layout()
    plt.show()

# ROI Generation
roi= None
roi_coord= None
roi_pt=None
def s_roi(click,release):
    global roi,roi_coord,roi_pt
    # check if roi is inside image
    if (click.xdata is None or click.ydata is None or release.xdata is None or release.ydata is None):
        return
    x1=int(round(min(click.xdata,release.xdata)))
    x2=int(round(max(click.xdata,release.xdata)))
    y1=int(round(min(click.ydata,release.ydata)))
    y2=int(round(max(click.ydata,release.ydata)))

    height, width= gray_img.shape[:2]
    if x2 <= x1 or y2 <= y1:
        print("Invalid Selection")

    roi= gray_img[y1:y2,x1:x2].copy()
    roi_pt=[y1,y2,x1,x2]
    #rectangle req (x,y,width,height)
    roi_coord= (x1,y1,x2-x1,y2-y1)
    print("ROI is registered")
    print("ROI Shape:",roi.shape)







#load train image
img_to_del=[]
f_path=choose_folder()
train_img=s_train_img(f_path)
img=cv2.imread(train_img)
if img is None:
    raise ValueError("Could not load image")
orgfile_name= os.path.basename(train_img)
file_dir= os.path.dirname(train_img)
print("Image Name: ",orgfile_name)
print("Image Folder Path: ",file_dir)

#cv2.imshow('image',img)


#convert to grayscale image
if img.ndim ==2:
    gray_img=img
    print("Image type: gray")
elif img.ndim == 3 and img.shape[2]==3:
    gray_img=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    print("Image type: BGR")
elif img.ndim == 3 and img.shape[2]==4:
    gray_img=cv2.cvtColor(img,cv2.COLOR_BGRA2GRAY)
    print("Image type: BGRA")
else:
    raise ValueError("Unsupported imge for conversion")


# ROI Generations
# Drag and generate

fig, ax = plt.subplots(figsize=(12,8))
ax.imshow (gray_img,cmap="gray")
ax.set_title("ROI_Selector | Close window after selecting the ROI")
ax.axis("off")
selector= RectangleSelector(
    ax,s_roi,
    useblit=True,
    button=[1],
    minspanx=3,
    minspany=3,
    spancoords="pixels",
    interactive=True,
    props={"facecolor":"none","edgecolor":"green","linewidth":2} )
fig.tight_layout()
plt.show()

fig, ax = plt.subplots(figsize=(12,8),linewidth=10, edgecolor='black')
ax.imshow (gray_img,cmap="gray")
ax.set_title("Reference Image")
ax.axis("off")
name="Reference.png"
img_to_del.append(name)
fig.savefig(name, dpi=200,edgecolor=fig.get_edgecolor())
fig.tight_layout()

fig, ax = plt.subplots(figsize=(12,8),linewidth=10, edgecolor='black')
ax.imshow (roi,cmap="gray")
ax.set_title("Trained Feature")
ax.axis("off")
name="Train.png"
img_to_del.append(name)
fig.savefig(name, dpi=200,edgecolor=fig.get_edgecolor())
fig.tight_layout()


#Processing
train_template=roi
SP=round(cv2.Laplacian(train_template,cv2.CV_64F).var(),2)
print("Sharpness ",SP)
BT=round(cv2.mean(train_template)[0],2)
print("Brightness ",BT)

# Define Specifications
while True:
    specifications=input("Accept the values of trained images as Specs? (y/n/e): ").lower()
    if specifications in ['y','n','e']:
        break
        print("Invalid Input. Enter 'y'='Yes' or 'n'='No' or 'e'='Exit'.")
if specifications=='y':
    spec_sharpness=SP-5
    spec_brightness=BT-5
elif specifications=='n':
    print("Custom Specifications")
    while True:
        try:
            spec_sharpness=float(input("Spec values for sharpness: "))
            break
        except ValueError:
            print("Invalid Input. Enter valid number.")
    while True:
        try:
            spec_brightness=float(input("Spec values for brightness: "))
            break
        except ValueError:
            print("Invalid Input. Enter valid number.")
else:
    print("Process aborted!")    

# Run Process
if specifications == 'y' or specifications=='n':

    while True:
        check=input("Proceed for batch processsing? (y/n): ").lower()
        if check in ['y','n']:
            break
        print("Invalid Input. Enter 'y' or 'n'.")
    if check == 'n':
        print("Batch processing aborted")
    else:
        Image_Name=[]
        Image_Type=[]
        Sharpness=[]
        Brightness=[]
        Feature_Matching=[]
        Feature_shift=[]
        Shift_X_val=[]
        Shift_Y_val=[]
        Result=[]
        for i in range (0,len(all_img_path)):
            # Read image
            b_img=cv2.imread(all_img_path[i])
            # Image data type
            if b_img is None:
                raise ValueError("Could not load image")
            file_name= os.path.basename(all_img_path[i])
            # Image name
            Image_Name.append(file_name)
            if b_img.ndim ==2:
                gray_img=b_img
                Image_Type.append("gray")
            elif b_img.ndim == 3 and b_img.shape[2]==3:
                gray_img=cv2.cvtColor(b_img,cv2.COLOR_BGR2GRAY)
                Image_Type.append("BGR")
            elif b_img.ndim == 3 and b_img.shape[2]==4:
                gray_img=cv2.cvtColor(b_img,cv2.COLOR_BGRA2GRAY)
                print("Image type: BGRA")
                Image_Type.append("BGRA")
            else:
                raise ValueError("Unsupported imge for conversion")
            # ROI image
            roi=gray_img[roi_pt[0]:roi_pt[1],roi_pt[2]:roi_pt[3]]
            # Sharpness
            SP=float(round(cv2.Laplacian(roi,cv2.CV_64F).var(),2))
            Sharpness.append(SP)
            # Brightness
            BT=float(round(cv2.mean(roi)[0],2))
            Brightness.append(BT)
            # Feature Shift
            
            result=cv2.matchTemplate(gray_img,train_template,cv2.TM_CCOEFF_NORMED)
            _, match_score, _, match_location = cv2.minMaxLoc(result)

            train_x=roi_coord[0]
            train_y=roi_coord[1]
            current_x, current_y = match_location

            shift_x = current_x - train_x
            shift_y = current_y - train_y
            Shift_X_val.append(shift_x)
            Shift_Y_val.append(shift_y)
            shift_distance = float(np.sqrt(shift_x**2 + shift_y**2))
            # Spec
            shift_spec = 10
            match_score_spec = 0.75

            Feature_Matching.append(round(match_score,2))
            Feature_shift.append(round(shift_distance,2))

            # Spec Comparision
            if spec_sharpness<SP and spec_brightness<BT and shift_spec>shift_distance and match_score_spec<match_score :
                Result.append("Pass")
            else:
                Result.append("Fail")

        data=[
            ("Sharpness",Sharpness,spec_sharpness),
            ("Brightness",Brightness,spec_brightness),
            ("Matching Score",Feature_Matching,match_score_spec),
            ("Feature Shift",Feature_shift,shift_spec),
        ]
        fig,axes=plt.subplots(2,2,figsize=(14,9))
        for ax,(title,value,spec) in zip(axes.flat,data):
            ax.plot(
                Image_Name,
                value,
                marker="o",
                linestyle="-",
                label=title,
            )
            ax.axhline(
                y=spec,
                linestyle="--",
                label=spec,
            )
            ax.set_title(title)
            ax.set_xlabel("Image Name")
            ax.set_ylabel(title)
            ax.tick_params(axis="x", labelrotation=45)
            ax.grid(True, linestyle=":", alpha=0.6)
            ax.legend()
        fig.suptitle("Result Monitoring", fontsize=16)
        plt.tight_layout()
        name="Chart.png"
        img_to_del.append(name)
        fig.savefig(name, dpi=200)
        #plt.show()



        print("Batch processing completed.")

        # Print CSV file
        csv_name="Trained image "+str(orgfile_name)+".csv"
        Header=["Image Name","Image Type","Sharpness","Brightness","Match Score","Shift (px)","Results"]\
            
            # "w"= creates a new file
            # "a"= adds a row
        with open(csv_name,"w",newline="",encoding="utf-8") as file:
                writer= csv.writer(file)
                writer.writerow(Header)
                for i in range (0,len(Image_Name)):
                    writer.writerow([Image_Name[i],
                                    Image_Type[i],
                                    Sharpness[i],
                                    Brightness[i],
                                    Feature_Matching[i],
                                    Feature_shift[i],
                                    Result[i]])
        print("CSV file generated!")




        # PDF
        pdf = FPDF(orientation="P", unit="mm", format="A4")
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_margins(left=15, top=15, right=15)
        pdf.set_title("Camera and Lighting Drift Monitor Report")
        pdf.set_author("Rishabh Negi")
        pdf.add_page()

        # Heading
        pdf.set_font("Times", style="B", size=24)
        pdf.set_text_color(30, 60, 120)
        ### pdf.cell(0,14)
        pdf.cell(0, 12,
                "Camera and Lighting Drift Monitor Report",
                    align="C",
                    new_x="LMARGIN",
                    new_y="NEXT")
        # Data
        ### pdf.cell(0,6)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", style="B", size=16)

        pdf.ln(8)
        pdf.cell(0,12,"Sharpness",new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", size=11)
        pdf.multi_cell(0, 6, "Image sharpness is the clarity," \
                        " crispness, and definition of fine details"
                        " and edges within a photograph or digital image.",
                    new_x="LMARGIN", new_y="NEXT")

        pdf.ln(8)
        pdf.set_font("Helvetica", style="B", size=16)
        pdf.cell(0,12,"Brightness",new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", size=11)
        pdf.multi_cell(0, 6, "Brightness measures the overall lightness or darkness " \
                        "of a digital image by changing red, green, and blue (RGB) " \
                        "pixel intensity values.",
                    new_x="LMARGIN", new_y="NEXT")

        pdf.ln(8)
        pdf.set_font("Helvetica", style="B", size=16)
        pdf.cell(0,12,"Feature Drift",new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", size=11)
        pdf.multi_cell(0, 6, "Image feature drift is a shift in the statistical distribution, " \
        "scale, sparsity, or visual characteristics of input image data"
        " in production compared to the baseline set used to train.",
                    new_x="LMARGIN", new_y="NEXT")

        pdf.ln(12)
        pdf.set_font("Helvetica", style="B", size=16)
        pdf.cell(0,8,"Trained Image:- "+file_name,new_x="LMARGIN", new_y="NEXT")
        pdf.ln(8)
        pdf.set_font("Helvetica", size=11)
        pdf.cell(0,8,"Secification Selected are as follows:- ",new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0,8,"Brightness: "+str(spec_brightness),new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0,8,"Sharpness: "+str(spec_sharpness),new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0,8,"shift_spec: "+str(shift_spec),new_x="LMARGIN", new_y="NEXT")

        # Image
        #pdf.image("img1.png", x=165, y=8, w=30)
        tw=pdf.w
        rm=pdf.r_margin
        lm=pdf.l_margin
        gap=5
        aval=tw-rm-lm
        img_w=(aval-gap)/2
        img_y=pdf.get_y()+12
        x1=lm
        x2=lm+gap+img_w
        pdf.image("Reference.png", x=x1, y=img_y, w=img_w)
        pdf.image("Train.png", x=x2, y=img_y, w=img_w)
        pdf.set_font("Helvetica", style="I", size=9)

        # Table
        pdf.add_page()
        pdf.cell(0,8,"Processed Data:- ",new_x="LMARGIN", new_y="NEXT")

        table_data=[Header]+list(zip(img_name,
                            Image_Type,
                            Sharpness,
                            Brightness,
                            Feature_Matching,
                            Feature_shift,
                            Result))
        with pdf.table() as table:
            for data_row in table_data:
                row = table.row()
                for datum in data_row:
                    row.cell(str(datum))

        # Graph
        with Image.open("chart.png") as img:
            img_w,img_h=img.size
        aval_w=pdf.w-pdf.l_margin-pdf.r_margin
        c_w=aval_w
        c_h=c_w*(img_h/img_w)
        c_y=pdf.get_y()+10
        aval_h=pdf.h-pdf.b_margin-c_y
        if c_h>aval_h:
            pdf.add_page()
            c_y=pdf.get_y()
        pdf.image("Chart.png", x=pdf.l_margin, y=c_y, w=c_w)
        pdf.output("report.pdf")

        for i in range (0,len(img_to_del)):
            os.remove(img_to_del[i])
        print("Batch processing completed.")

