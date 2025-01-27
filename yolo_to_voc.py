#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 17 22:10:01 2018

@author: Caroline Pacheco do E. Silva
"""

import os
import cv2
from xml.dom.minidom import parseString
from lxml.etree import Element, SubElement, tostring
import numpy as np
from os.path import join

## coco classes
YOLO_CLASSES = ("Cross_crack","Dry_shouldering","Micro_crack"
                ,"Non_defective_cell","Pin_crack","Solar_Cell",
                "dark_area","dead_cell"
)

## converts the normalized positions  into integer positions
def unconvert(class_id, width, height, x, y, w, h):

    xmax = int((x*width) + (w * width)/2.0)
    xmin = int((x*width) - (w * width)/2.0)
    ymax = int((y*height) + (h * height)/2.0)
    ymin = int((y*height) - (h * height)/2.0)
    class_id = int(class_id)
    return (class_id, xmin, xmax, ymin, ymax)


## path root folder
ROOT = 'coco'


## converts coco into xml 
def xml_transform(root, classes):  
    class_path  = join(root, 'labels')
    ids = list()
    l=os.listdir(class_path)
    print("l",l)
    
    check = '.DS_Store' in l
    if check == True:
        l.remove('.DS_Store')
        
    ids=["".join(x.split('.')[0:-1]) for x in l]   
    print("ids",ids)

    annopath = join(root, 'labels', '%s.txt')
    imgpath = join(root, 'images', '%s.jpg')
    
    os.makedirs(join(root, 'outputs'), exist_ok=True)
    outpath = join(root, 'outputs', '%s.xml')
    error_images=[]
    error_annotation=[]
    for number,i in enumerate(range(len(ids))):
        img_id = ids[i]
        print("enumerate number",number)
        print("img_id",img_id) 
        if img_id == "classes":
            print("inside img_id clause")
            continue
        if os.path.exists(outpath % img_id):
            continue
        print(imgpath % img_id)
        try:
            img= cv2.imread(imgpath % img_id)
            print("img",img.shape)
            height, width, channels = img.shape # pega tamanhos e canais das images
        except:
            error_images.append(img_id)
            continue

        node_root = Element('annotation')
        node_folder = SubElement(node_root, 'folder')
        node_folder.text = 'VOC2007'
        img_name = img_id + '.jpg'
    
        node_filename = SubElement(node_root, 'filename')
        node_filename.text = img_name
        
        node_source= SubElement(node_root, 'source')
        node_database = SubElement(node_source, 'database')
        node_database.text = 'Coco database'
        
        node_size = SubElement(node_root, 'size')
        node_width = SubElement(node_size, 'width')
        node_width.text = str(width)
    
        node_height = SubElement(node_size, 'height')
        node_height.text = str(height)

        node_depth = SubElement(node_size, 'depth')
        node_depth.text = str(channels)

        node_segmented = SubElement(node_root, 'segmented')
        node_segmented.text = '0'

        target = (annopath % img_id)
        if os.path.exists(target):
            try :
                label_norm= np.loadtxt(target).reshape(-1, 5)
            except:
                error_annotation.append(img_id)
                os.remove(imgpath % img_id)
                continue

            for i in range(len(label_norm)):
                labels_conv = label_norm[i]
                new_label = unconvert(labels_conv[0], width, height, labels_conv[1], labels_conv[2], labels_conv[3], labels_conv[4])
                node_object = SubElement(node_root, 'object')
                node_name = SubElement(node_object, 'name')
                node_name.text = classes[new_label[0]]
                
                node_pose = SubElement(node_object, 'pose')
                node_pose.text = 'Unspecified'
                
                
                node_truncated = SubElement(node_object, 'truncated')
                node_truncated.text = '0'
                node_difficult = SubElement(node_object, 'difficult')
                node_difficult.text = '0'
                node_bndbox = SubElement(node_object, 'bndbox')
                node_xmin = SubElement(node_bndbox, 'xmin')
                node_xmin.text = str(new_label[1])
                node_ymin = SubElement(node_bndbox, 'ymin')
                node_ymin.text = str(new_label[3])
                node_xmax = SubElement(node_bndbox, 'xmax')
                node_xmax.text =  str(new_label[2])
                node_ymax = SubElement(node_bndbox, 'ymax')
                node_ymax.text = str(new_label[4])
                xml = tostring(node_root, pretty_print=True)  
                dom = parseString(xml)
        print(xml)  
        f =  open(outpath % img_id, "wb")
        #f = open(os.path.join(outpath, img_id), "w")
        #os.remove(target)
        f.write(xml)
        f.close()     
    print("error_images",error_images,len(error_images))
    print("error_annotaion",error_annotation,len(error_annotation))


xml_transform(ROOT, YOLO_CLASSES)

