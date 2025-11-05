import numpy as np
import pandas as pd
import csv
import h5py
import matplotlib.pyplot as plt
import sys
import zipfile
import os
import ActiveFlagger as acf
from eigsep_data.utils import lin2dB, mlin

def isfilenormal(fname, lowo = -5, higho = 0,lows = -5, highs = 0, highl = -30,
                 highd = -5, highr = -5, higha = -5, highal = -30, highn = -30):
  weird = {}
  good = True
  data, cal, head, meta = eo.io.read_s11_file(fname)
  vnao = acf.mlin(cal["VNAO"])
  vnas = acf.mlin(cal["VNAS"])
  vnal = asf.mlin(cal["VNAL"])
  if lowo > vnao:
    good = False
  elif higho < vnao:
    good = False
  if lows > vnas:
    good = False
  elif highs < vnas:
    good = False
  if highl < vnal:
    good = False
  weird.update({"cal": good})
  if len(data) == 1:
    rec = asf.mlin(data["rec"])
    if highr < rec:
      good = False
    weird.update({"rec": bool(highr > rec)})
  else:
    ante = asf.mlin(data["ant"])
    load = asf.mlin(data["load"])
    loud = asf.mlin(data["noise"])
    if higha < ante:
      good = False
    if highal < load:
      good = False
    if highn < loud:
      good = False
    weird.update({"ant": bool(higha > ante)})
    weird.update({"load": bool(highal > load)})
    weird.update({"noise": bool(highn > loud)})
  return good, weird

def isfoldernormal(s11folder, lowo = -5, higho = 0,lows = -5, highs = 0,
                   highl = -30, highd = -5, highr = -5, higha = -5, highal = -30,
                   highn = -30): 
  # -- Documentation--
  # Required Inputs: A folder containing only s11 files; if you have other stuff in there, should remove it first.
  # Optional Inputs: The upper and lower bounds of each input.
  # Outputs: A boolean value denoting normality; if true, the entire folder is normal.
  #          A dictionary of anomalies, structured as such:
  #          {"path + filename": {"datacategory": bool}}
  fdic = {}
  for path, folders, files in os.walk(s11folder):
    for fname in files:
      fpath = path + "/" + fname
      discard, keep = isfilenormal(fpath, lowo, higho, lows, highs, highl, highd, highr, higha, highal, highn)
      fdic.update({fpath: keep})
  return fdic

def dataanomalies(tingy): # Notes files in which the calibration is normal but the data is not. Takes results of isfoldernormal.
  l = []
  for d in tingy:
    if len(tingy[d]) == 2:
      b = tingy[d]["rec"]
    else:
      b = tingy[d]["ant"] and tingy[d]["load"] and tingy[d]["noise"]
    if b != tingy[d]["cal"]:
      l.append(d)
  return l

def isfoldernormalfordisplay(s11folder, lowo = -5, higho = 0,lows = -5, highs = 0,
                   highl = -30, highd = -5, highr = -5, higha = -5, highal = -30,
                   highn = -30, complain = True, displayAno = False, displayAll = False):
  # -- Documentation--
  # Required Inputs: A folder containing only s11 files; if you have other stuff in there, should remove it first.
  # Optional Inputs: The upper and lower bounds of each input.
  #                  The option of a written summary of anomalies; defaults to true.
  #                  The option to see the plotted graphs of either the anomalous values or all values of
  #                  anomalous graphs.
  # Outputs: A boolean value denoting normality; if true, the entire folder is normal.
  #          A dictionary of anomalies, structured as such:
  #          {"path + filename": [[Written list of anomalies], [Key to the anomalous data]]}
  #          Example: {"/C:/S11F/f.h5": [["Mean VNAO is above -5.", "Mean VNAS is above -5."], ["VNAO", "VNAS"]]}
  if displayAll or displayAno: # A reminder about The Annoying TM.
    print("Depending on your terminal, you may need to open XQuartz or a similar platform to see graphs. Sorry!")
  complaints = {}
  normal = True
  # Go through the folder and evaluate each file.
  for path, folders, files in os.walk(s11folder):
    for fname in files: # Get each file.
      whining = []
      yapping = []
      good = True
      data, cal, head, meta = eo.io.read_s11_file(path + "/" + fname)
      # First, check the calibration.
      vnao = asf.mlin(cal["VNAO"])
      vnas = asf.mlin(cal["VNAS"])
      vnal = asf.mlin(cal["VNAL"])
      if lowo > vnao:
        whining.append("Mean VNAO " + str(vnao) + " is below " + str(lowo) + ".")
        yapping.append("VNAO")
        good = False
      elif higho < vnao:
        whining.append("Mean VNAO " + str(vnao) + " is above " + str(higho) + ".")
        yapping.append("VNAO")
        good = False
      if lows > vnas:
        whining.append("Mean VNAS " + str(vnas) + " is below " + str(lows) + ".")
        yapping.append("VNAS")
        good = False
      elif highs < vnas:
        whining.append("Mean VNAS " + str(vnas) + " is above " + str(highs) + ".")
        yapping.append("VNAS")
        good = False
      if highl < vnal:
        whining.append("Mean VNAL " + str(vnal) + " is above " + str(highl) + ".")
        yapping.append("VNAL")
        good = False
      # Second, check the data.
      if len(data) == 1:
        rec = asf.mlin(data["rec"])
        if highr < rec:
          whining.append("Mean data " + str(rec) + " is above " + str(highr) + ".")
          yapping.append("rec")
          good = False
      else:
        ante = asf.mlin(data["ant"])
        load = asf.mlin(data["load"])
        loud = asf.mlin(data["noise"])
        if higha < ante:
          whining.append("Mean antenna data " + str(ante) + " is above " + str(higha) + ".")
          yapping.append("ant")
          good = False
        if highal < load:
          whining.append("Mean load data " + str(load) + " is above " + str(highal) + ".")
          yapping.append("load")
          good = False
        if highn < loud:
          whining.append("Mean noise " + str(loud) + " is above " + str(highn) + ".")
          yapping.append("noise")
          good = False
      # Finally, summarize the complaints.
      if not good:
        fpath = path + "/" + fname
        complaints.update({fpath : [whining, yapping]})
        normal = False
  # Take all the complaints and display them appropriately.
  if not normal:
    if complain or displayAll or displayAno:
      print("The following is a complete list of abnormal files and their anomalies in this folder.")
    for fiel in complaints:
      if complain:
        print("  +  " + fiel)
        for whine in complaints[fiel][0]:
          print("    -  " + whine)
      if displayAno or displayAll:
        colors = {"VNAO": "red", "VNAS": "orange", "VNAL": "yellow",
                "ant": "green", "load": "blue", "noise": "purple",
                "rec": "gray"} # Yes, it IS completely necessay to have a different color for each one!
        data, cal, head, meta = eo.io.read_s11_file(fiel)
        plt.figure()
        if displayAno and not displayAll: # If only the anomalies are wanted, just pull from the complaints.
          for yap in complaints[fiel][1]:
            if yap[:3] == "VNA":
              plt.plot(lin(cal[yap]), color = colors[yap],label = yap)
            else:
              plt.plot(lin(data[yap]), color = colors[yap],label = yap)
        if displayAll: # Otherwise, display all of the lines.
          for yap in colors:
            if yap[:3] == "VNA":
              plt.plot(lin(cal[yap]), color = colors[yap],label = yap)
            else:
              if len(data) == 1 and yap == "rec":
                plt.plot(lin(data[yap]), color = colors[yap],label = yap)
              elif len(data) == 3 and yap != "rec":
                plt.plot(lin(data[yap]), color = colors[yap],label = yap)
        titl = fiel
        if displayAno:
          titl = fiel + " Anomalies"
        plt.title(titl)
        plt.legend()
        plt.show()
  if normal and complain:
    print("Nothing abnormal here!")
    # This will probably never occur unless there is very little in the folder or the code is broken.
  return normal, complaints
