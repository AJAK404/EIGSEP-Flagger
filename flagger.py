import numpy as np
import pandas as pd
import h5py
import matplotlib.pyplot as plt
import sys
import zipfile
import os

def lin(x):
  return 20 * np.log10(np.abs(x))

def mlin(x):
  return np.mean(lin(x))

def activeflag(data, cal, lowo = -5, higho = 0,lows = -5, highs = 0, highl = -30,
               highd = -5, highr = -5, higha = -5, highal = -30, highn = -30):
  # Checks normalacy as data is recorded after required amount of data; is either whole or scrolling.
  flags = {}
  vnao = np.mean(20 * np.log10(np.abs(cal["VNAO"])))
  vnas = np.mean(20* np.log10(np.abs(cal["VNAS"])))
  vnal = np.mean(20* np.log10(np.abs(cal["VNAL"])))
  good = True
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
  flags.update({"cal": good})
  if len(data) == 1:
    rec = np.mean(20* np.log10(np.abs(data["rec"])))
    rnorm = bool(highr > rec)
    flags.update({"rec": rnorm})
  else:
    ante = np.mean(20* np.log10(np.abs(data["ant"])))
    load = np.mean(20* np.log10(np.abs(data["load"])))
    loud = np.mean(20* np.log10(np.abs(data["noise"])))
    anorm = bool(higha > ante)
    alnorm = bool(highal > load)
    nnorm = bool(highn > loud)
    flags.update({"ant": anorm, "load": alnorm, "noise": nnorm})
  return flags
