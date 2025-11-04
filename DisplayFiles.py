import numpy as np
import pandas as pd
import csv
import h5py
import matplotlib.pyplot as plt
import sys
import zipfile
import os
import ActiveFlagger as acf

def listanomalies(anomalies): # Takes complaints and lists them.
  if anomalies == {}:
    print("Nothing abnormal here!")
  for fiel in anomalies:
    print("  +  " + fiel)
    for whine in anomalies[fiel][0]:
      print("    -  " + whine)

def displayAnomalies(anomalies, justAnomalies = False): # Takes anomalies and graphs them.
  colors = {"VNAO": "red", "VNAS": "orange", "VNAL": "yellow",
            "ant": "green", "load": "blue", "noise": "purple",
            "rec": "gray"} # Yes, it IS completely necessay to have a different color for each one!
  for fiel in anomalies:
    data, cal, head, meta = eo.io.read_s11_file(fiel)
    plt.figure()
    if justAnomalies: # If only the anomalies are wanted, just pull from the complaints.
      for yap in anomalies[fiel][1]:
        if yap[:3] == "VNA":
          plt.plot(acf.lin(cal[yap]), color = colors[yap],label = yap)
        else:
          plt.plot(acf.lin(data[yap]), color = colors[yap],label = yap)
    else: # Otherwise, display all of the lines.
      for yap in colors:
        if yap[:3] == "VNA":
          plt.plot(acf.lin(cal[yap]), color = colors[yap],label = yap)
        else:
          if len(data) == 1 and yap == "rec":
            plt.plot(acf.lin(data[yap]), color = colors[yap],label = yap)
          elif len(data) == 3 and yap != "rec":
            plt.plot(acf.lin(data[yap]), color = colors[yap],label = yap)
    titl = fiel
    if justAnomalies:
      titl = fiel + " Anomalies"
    plt.title(titl)
    plt.legend()
    plt.show()

def displayNormal(s11folder, anomalies): # Takes normal data and graphs it.
  colors = {"VNAO": "red", "VNAS": "orange", "VNAL": "yellow",
            "ant": "green", "load": "blue", "noise": "purple",
            "rec": "gray"} # Yes, it IS completely necessay to have a different color for each one!
  # Go through the folder and evaluate each file.
  for path, folders, files in os.walk(s11folder):
    for fname in files: # Get each file.
      fpath = path + "/" + fname
      try: # If this actually works, the data is abnormal.
        thing = anomalies[fpath]
      except: # If the data is not abnormal, it is normal and we ought to plot it.
        data, cal, head, meta = eo.io.read_s11_file(fpath)
        plt.figure()
        for yap in colors:
          if yap[:3] == "VNA":
            plt.plot(acf.lin(cal[yap]), color = colors[yap],label = yap)
          else:
            if len(data) == 1 and yap == "rec":
              plt.plot(acf.lin(data[yap]), color = colors[yap],label = yap)
            elif len(data) == 3 and yap != "rec":
              plt.plot(acf.lin(data[yap]), color = colors[yap],label = yap)
        titl = fpath
        plt.title(titl)
        plt.legend()
        plt.show()

def displayAll(s11folder): # Displays all the graphs.
  colors = {"VNAO": "red", "VNAS": "orange", "VNAL": "yellow",
            "ant": "green", "load": "blue", "noise": "purple",
            "rec": "gray"} # Yes, it IS completely necessary to have a different color for each one!
  for path, folders, files in os.walk(s11folder):
    for fname in files: # Get each file.
        fpath = path + "/" + fname
        data, cal, head, meta = eo.io.read_s11_file(fpath)
        plt.figure()
        for yap in colors:
          if yap[:3] == "VNA":
            plt.plot(acf.lin(cal[yap]), color = colors[yap],label = yap)
          else:
            if len(data) == 1 and yap == "rec":
              plt.plot(acf.lin(data[yap]), color = colors[yap],label = yap)
            elif len(data) == 3 and yap != "rec":
              plt.plot(acf.lin(data[yap]), color = colors[yap],label = yap)
        titl = fpath
        plt.title(titl)
        plt.legend()
        plt.show()

def countFiles(s11folder): # Counts all the files in the folder.
  f = 0
  for path, folders, files in os.walk(s11folder):
    for fname in files: # Get each file.
      f += 1
  return f

def shows11(fpath):
  data, cal, head, meta = eo.io.read_s11_file(fpath)
  plt.figure()
  colors = {"VNAO": "red", "VNAS": "orange", "VNAL": "yellow",
            "ant": "green", "load": "blue", "noise": "purple",
            "rec": "gray"} # Yes, it IS completely necessary to have a different color for each one!
  for yap in colors:
    if yap[:3] == "VNA":
      plt.plot(acf.lin(cal[yap]), color = colors[yap],label = yap)
    else:
      if len(data) == 1 and yap == "rec":
        plt.plot(acf.lin(data[yap]), color = colors[yap],label = yap)
      elif len(data) == 3 and yap != "rec":
        plt.plot(acf.lin(data[yap]), color = colors[yap],label = yap)
  titl = fpath
  plt.title(titl)
  plt.legend()
  plt.show()
