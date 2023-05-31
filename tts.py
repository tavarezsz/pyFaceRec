from tkinter import *
from PIL import Image, ImageTk
import cv2
import customtkinter as ck

# Create an instance of TKinter Window or frame
ck.set_appearance_mode("Dark")
ck.set_default_color_theme("blue")
win = ck.CTk()

# Set the size of the window
win.geometry("700x350")

# Create a Label to capture the Video frames
label =Label(win)
label.pack()
cap= cv2.VideoCapture(0)

# Define function to show frame
def show_frames():
   # Get the latest frame and convert into Image
   cv2image= cv2.cvtColor(cap.read()[1], cv2.COLOR_BGR2RGB)
   cv2image = cv2.flip(cv2image,1)
   img = Image.fromarray(cv2image)
   # Convert image to PhotoImage
   imgtk = ImageTk.PhotoImage(image = img)
   label.imgtk = imgtk
   label.configure(image=imgtk)
   # Repeat after an interval to capture continiously
   label.after(20, show_frames)

button = Button(win,text='botão', command=show_frames)
button.pack()

win.mainloop()
