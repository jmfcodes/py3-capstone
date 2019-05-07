#!/usr/bin/env python
# coding: utf-8

# goal: search through the images looking for the occurrences of keywords and faces.
# 1. for each individual file:
# 2. read text & make it searchable
# 3. when keyword is found, make a contact sheet of faces

import zipfile

from PIL import Image
from PIL import ImageDraw
import pytesseract
import cv2 as cv
import numpy as np
import os

# loading the face detection classifier
face_cascade = cv.CascadeClassifier('readonly/haarcascade_frontalface_default.xml')

# location of zip & directory
targetzip = 'readonly/images.zip'
targetdir = 'imagesdir/'

# extract files
with zipfile.ZipFile(targetzip,"r") as zip_ref:
    zip_ref.extractall(targetdir)


def read_text(img):
    return pytesseract.image_to_string(img).lower()


def get_faces(file):
    # from img file, add all faces to a list & return that list

    img = cv.imread(file)
    # convert to grayscale
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.18)

    pil_img=Image.fromarray(gray,mode="L")

    drawing=ImageDraw.Draw(pil_img)

    images = []
    # make a copy of the file for cropping
    wholepage = Image.open(file)
    for x,y,w,h in faces:
        # draw around each face
        drawing.rectangle((x,y,x+w,y+h), outline="red")

        # crop each face to add to the list
        face = wholepage.crop((x,y,x+w,y+h))
        images.append(face)

    return images


def contact_sheet(images):
    # find the largest image to use as the basis for the size of the contact sheet
    largest_x, largest_y = max(image.size for image in images)
    count = len(images)

    # create blank contact sheet canvas
    first_image=images[0]
    contact_sheet=Image.new('L', (largest_x*5, largest_y*(int(count/5) + (21 % 5 > 0))))
    x=0
    y=0

    # add images to contact sheet
    for img in images:
        contact_sheet.paste(img, (x, y) )
        # update position for next image:
        if x+largest_x == contact_sheet.width:
            x=0
            y=y+largest_y
        else:
            x=x+largest_x

    # resize and display contact sheet
    contact_sheet = contact_sheet.resize((int(contact_sheet.width/2),int(contact_sheet.height/2) ))
    display(contact_sheet)


def get_search_term():
    SEARCH_TERM = input("Enter a search term: ")
    if len(SEARCH_TERM) == 0:
        SEARCH_TERM = 'michigan'
    return SEARCH_TERM.lower()


def read_all_files():
    # create a dict where k:v == file_name:text
    files_and_text = {}
    for file in os.listdir(targetdir):
        files_and_text[file] = read_text(targetdir + file)
    return files_and_text


def search_files(SEARCH_TERM, files_and_text):
    target_files = [key for (key, value) in files_and_text.items() if SEARCH_TERM in value]
    if len(target_files) == 0:
        print('Sorry, the search term ** {} ** was not found.'.format(SEARCH_TERM))
    for file in target_files:
        faces = get_faces(targetdir + file)
        if len(faces) == 0:
            print('No faces found in file {}.'.format(file))
        else:
            print('\nSearch term: {}.\nFaces found in file {}:'.format(SEARCH_TERM, file))
            contact_sheet(get_faces(targetdir + file))


# main
SEARCH_TERM = get_search_term()
print("Please wait...")
files_and_text = read_all_files()
search_files(SEARCH_TERM, files_and_text)
