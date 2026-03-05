import webbrowser
import io
import base64
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import eigsep_observing as eo
from ActiveFlagger import activeflag
from eigsep_observing import EigsepRedis
import time
import webbrowser
import subprocess
import threading
from datetime import datetime
from eigsep_corr.utils import calc_times, calc_freqs_dfreq
import matplotlib.dates as mdates

class Website: 
  flag = True # Tells functions running on a loop to stop when flag is false.
  r2 = EigsepRedis(host="10.10.10.10") # For spectrum.
  r = EigsepRedis(host="10.10.10.11") # For metadata and S11 data.
  #r= EigsepRedis(host="192.168.10.83")
  readspec = [] # Contains all spectrum data. 
  tdata = np.array([[[0],[0]], [[0],[0]], [[0],[0]], [[0],[0]]]) # Contains the points for, in this order,
  #the monitored temperature A and B and the control temperature A and B, with time as the first coordinate.
  #This empty placeholder provides a base and is not plotted.
  data = {"ant": [0], "load": [0], "noise": [0], "rec": [0]} # Contains the S11 data; this empty placeholder avouds keyerrors.
  cal = {"VNAO": [0], "VNAS": [0], "VNAL": [0]} # Contains the S11 calibration data; this empty placeholder avoids keyerrors.
  opene = False # Denotes whether the website has been opened or not.
  mlist = [[0], [0], {"A_status": "error", "B_status": "error", "A_timestamp":0, "A_temp":0, "B_timestamp":0, "B_temp":0}, 
           {"A_status": "error", "B_status": "error", "A_timestamp":0, "A_T_now":0, "B_timestamp":0, "B_T_now":0}, {"distance_m": 0}, 
           {"az_pos": 0, "el_pos": 0}, {"sw_state":0}] # Contains metadata; this empty placeholder avoids keyerrors. 
  ks = ["0", "02", "04", "1", "13", "15", "2", "24", "3", "35", "4", "5"] # A list of all possible spectra.
  spec={"0": np.array([[0]]), "02": np.array([[0]]), "04": np.array([[0]]), "1": np.array([[0]]), "13": np.array([[0]]), "15": np.array([[0]]), 
        "2": np.array([[0]]), "24": np.array([[0]]), "3": np.array([[0]]), "35": np.array([[0]]), "4": np.array([[0]]), "5": np.array([[0]])}
  # Contains graphable spectrum data; this empty placeholder avoids keyerrors.
  freqs = [0]
  
  @classmethod
  def lin(cls, x): # Linearizes the datapoints in x.
    return 20* np.log10(np.abs(x))

  @classmethod
  def seefile(cls, data, cal): # Plots the S11 data.
    plt.figure(figsize=(6.4,3.5))
    colors = {"VNAO": "red", "VNAS": "orange", "VNAL": "yellow",
              "ant": "green", "load": "blue", "noise": "purple",
              "rec": "gray"} # Yes, it IS completely necessary to have a different color for each one!
    for yap in colors: # Goes through each key in data.
      if yap[:3] == "VNA": # If the key begins with VNA, it is in cal, and should be taken as such.
        plt.plot(cls.lin(cal[yap]), color = colors[yap],label = yap)
      else: # Otherwise, it is in data.
        if len(data) == 1 and yap == "rec": # If it is rec, and data contains rec, plot it.
          plt.plot(cls.lin(data[yap]), color = colors[yap],label = yap)
        elif len(data) == 3 and yap != "rec": # If it is not rec, and the data does not contain rec, plot it.
          plt.plot(cls.lin(data[yap]), color = colors[yap],label = yap)
    plt.title("S11")
    plt.tight_layout()
    plt.xlabel("Frequency (MHz)")
    plt.ylabel("|S11| (dB)")
    plt.legend()
    plt.tight_layout()
    buffer = io.BytesIO() # All the following converts the image of the plot to a string.
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    img64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    return img64 # Returns the image as a string.

  @classmethod
  def grabs11(cls): # Grabs S11 data on the S11 thread.
    while cls.flag: # Stops when the program ends.
      d, c, h, m = cls.r.read_vna_data() # Gets data, cal, header, and metadata.
      cls.data = d
      cls.cal = c
  
  @classmethod
  def grabbit(cls): # Grabs metadata on the metadata thread.
    while cls.flag:
      meta = cls.r.get_live_metadata()
      tem = meta["temp_mon"]
      tec = meta["tempctrl"]
      cls.tdata = np.append(cls.tdata, [[[datetime.fromtimestamp(tem["A_timestamp"])], [tem["A_temp"]]], 
                                        [[datetime.fromtimestamp(tem["B_timestamp"])], [tem["B_temp"]]],
                                        [[datetime.fromtimestamp(tec["A_timestamp"])], [tec["A_T_now"]]], 
                                        [[datetime.fromtimestamp(tec["B_timestamp"])], [tec["B_T_now"]]]], axis = 2)
      # Adds a datapoint of format (datetime, temperature) to the temperature array.
      cls.mlist = [meta["imu_antenna"], meta["imu_panda"], meta["temp_mon"], meta["tempctrl"], meta["lidar"], meta["motor"], meta["rfswitch"]]
      time.sleep(.1) # Limits rate of metadata grabbing.
      #print("Metadata in grabbing thread: \n" + str(cls.mlist))

  @classmethod
  def grabbe(cls): # Get each part of metadata for the website in a conveinet manner.
    #print("Metadata in main thread to page: \n" + str(cls.mlist))
    return cls.mlist[0], cls.mlist[1], cls.mlist[2], cls.mlist[3], cls.mlist[4], cls.mlist[5], cls.mlist[6],
  
  @classmethod
  def seetemp(cls): # Graphs the temperature.
    if len(cls.tdata) > 1200: # Graphs the last 1200 temperatures recorded.
      x = len(cls.tdata) - 1200
    else: # If 1200 temperatures do not exist, graphs what is there.
      x = 0
    plt.figure(figsize=(6.4,3.5))
    if cls.mlist[2]["A_status"] != "error": # Does not plot if there is an error.
      atm = cls.tdata[0][cls.tdata[0][x:, 0].argsort()]
      plt.scatter(atm[0][1:], atm[1][1:], color = "red",label = "A_Temp_Mon")
    if cls.mlist[2]["B_status"] != "error":
      btm = cls.tdata[1][cls.tdata[1][x:, 0].argsort()]
      plt.scatter(btm[0][1:], btm[1][1:], color = "orange",label = "B_Temp_Mon")
    if cls.mlist[3]["A_status"] != "error":
      atc = cls.tdata[2][cls.tdata[2][x:, 0].argsort()]
      plt.scatter(atc[0][1:], atc[1][1:], color = "green",label = "A_Temp_Ctrl")
    if cls.mlist[3]["B_status"] != "error":
      btc = cls.tdata[3][cls.tdata[3][x:, 0].argsort()]
      plt.scatter(btc[0][1:], btc[1][1:], color = "blue",label = "B_Temp_Ctrl")
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
    plt.gca().xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M:%S"))
    plt.xticks(rotation=90)
    plt.xlabel("Time")
    plt.ylabel("Temperature (C)")
    plt.title("Temperature")
    plt.tight_layout()
    plt.legend(loc="lower left")
    buffer = io.BytesIO() # Converts image of plot to a string.
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    img64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    return img64
  
  @classmethod
  def seespec(cls):
    plt.figure(figsize=(6.4,3.5))
    #print(len(cls.freqs))
    #print(len(np.log10(np.abs(cls.spec["1"][0]))))
    for k in ["0", "02", "04", "1", "13", "15", "2", "24", "3", "35", "4", "5"]:
      if len(cls.freqs) == len(np.log10(np.abs(cls.spec[k][0]))):
        plt.plot(cls.freqs, np.log10(np.abs(cls.spec[k][0])), label=k)
    plt.title("Spectra")
    plt.legend(loc="upper left")
    plt.xlabel("Frequency (MHz)")
    plt.ylabel("Power (log(counts))")
    plt.tight_layout()
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    img64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    return img64

  @classmethod
  def seespectrum(cls, ks):
    while cls.flag:
      # global IMGGGG
      cls.readspec = cls.r2.read_corr_data(timeout = 3)
      header = cls.r2.get_corr_header()
      cls.freqs, dfreq = calc_freqs_dfreq(header["sample_rate"], header["nchan"])
      cls.spec = eo.io.reshape_data(cls.readspec[2])
  
  def ripper(fname):
    i= -4
    chara = fname[i]
    fn = ""
    while chara != "/" and abs(i) <= len(fname):
      fn = chara + fn
      i -= 1
      try:
        chara = fname[i]
      except:
        return fn
    return fn
  
  @classmethod
  def buildpage(cls, meta={}, data={}, cal={}, spec = {}, fname="", active=False, path="."):
    # global opene
    # global IMGGGG
    if not active:
      normal = activeflag(data,cal)
      mia = meta["imu_antenna"]
      mip = meta["imu_panda"]
      tem = meta["temp_mon"]
      tec = meta["tempctrl"]
      lid = meta["lidar"]
      mot = meta["motor"]
      rfs = meta["rfswitch"]
    if active:
      try:       
        mia, mip, tem, tec, lid, mot, rfs = cls.grabbe()
      except KeyError:
        print("No metadata being collected; this is going to cause problems!")
        mia, mip, tem, tec, lid, mot, rfs = [0], [0], {"A_status": "error", "B_status": "error", "A_timestamp":0, "A_temp":0, "B_timestamp":0, "B_temp":0}, {"A_status": "error", "B_status": "error", "A_timestamp":0, "A_T_now":0, "B_timestamp":0, "B_T_now":0}, {"distance_m": 0}, {"az_pos": 0, "el_pos": 0}, {"sw_state":0}
      normal = activeflag(cls.data, cls.cal)
    else:
      tdata = np.append(tdata, [[[tem["A_timestamp"]], [tem["A_temp"]]], [[tem["B_timestamp"]], [tem["B_temp"]]],
                              [[tec["A_timestamp"]], [tec["A_T_now"]]], [[tec["B_timestamp"]], [tec["B_T_now"]]]], axis = 2)
    tgraph = """
      <img src="data:image/png;base64,""" + cls.seetemp() + """" width="90%">
      """
    terror = """"""
    if True:
      for boo in ["A_status", "B_status"]:
        if tem[boo] == "error":
          terror += """
        <p>Error in monitoring """ + boo + """</p>
           """
        if tec[boo] == "error":
          terror += """
        <p>Error in control """ + boo + """</p>
            """
    if True:
      if len(normal) == 2:
        dlist = """Recording: """ + str(normal["rec"]) + """</p>
      """
      else:
        dlist = """Antenna: """ + str(normal["ant"]) + """, Load: """ + str(normal["load"]) + """, Noise: """ + str(normal["noise"]) + """</p>
      """
    if active:
      if cls.cal["VNAO"] == [0] and len(cls.cal) == 1:
        imtab = """
    <div class="boxes" id="s11">
      <p>No VNA data yet!</p>
    </div>
      """
      else:
        imtab = """
    <div class="boxes" id="s11">
      <img src="data:image/png;base64,""" + cls.seefile(cls.data, cls.cal) + """" width="90%">
      <p>Calibration: """ + str(normal["cal"]) + """, """ + dlist + """
    </div>
      """
      # stab = "" <img src="data:image/png;base64,""" + cls.seeactives11() + """" width="90%">
      # sbutton = ""
      # specfunc = ""
      #  
      stab = """
    <div class="boxes" id="spec">
    """ + """
      <img id="g" class="gs" style.display="block" src="data:image/png;base64,""" + cls.seespec() + """" width="90%"> 
    </div>
    """
      # <button onclick="showhide('gall')">All</button>
      # <button onclick="showhide('g0')">0</button>
      # <button onclick="showhide('g02')">02</button>
      # <button onclick="showhide('g04')">04</button>
      # <button onclick="showhide('g1')">1</button>
      # <button onclick="showhide('g13')">13</button>
      # <button onclick="showhide('g15')">15</button>
      # <button onclick="showhide('g2')">2</button>
      # <button onclick="showhide('g24')">24</button>
      # <button onclick="showhide('g3')">3</button>
      # <button onclick="showhide('g35')">35</button>
      # <button onclick="showhide('g4')">4</button>
      # <button onclick="showhide('g5')">5</button>
      # <img id="gall" class="gs" display="block" src="data:image/png;base64,""" + kimgs["all"] + """" width="90%">
      # <img id="g0" class="gs" display="none" src="data:image/png;base64,""" + kimgs["0"] + """" width="90%"> 
      # <img id="g02" class="gs" display="none" src="data:image/png;base64,""" + kimgs["02"] + """" width="90%"> 
      # <img id="g04" class="gs" display="none" src="data:image/png;base64,""" + kimgs["04"] + """" width="90%"> 
      # <img id="g1" class="gs" display="none" src="data:image/png;base64,""" + kimgs["1"] + """" width="90%">
      # <img id="g13" class="gs" display="none" src="data:image/png;base64,""" + kimgs["13"] + """" width="90%"> 
      # <img id="g15" class="gs" display="none" src="data:image/png;base64,""" + kimgs["15"] + """" width="90%"> 
      # <img id="g2" class="gs" display="none" src="data:image/png;base64,""" + kimgs["2"] + """" width="90%"> 
      # <img id="g24" class="gs" display="none" src="data:image/png;base64,""" + kimgs["24"] + """" width="90%">  
      # <img id="g3" class="gs" display="none" src="data:image/png;base64,""" + kimgs["3"] + """" width="90%">  
      # <img id="g35" class="gs" display="none" src="data:image/png;base64,""" + kimgs["35"] + """" width="90%">  
      # <img id="g4" class="gs" display="none" src="data:image/png;base64,""" + kimgs["4"] + """" width="90%">
      # <img id="g5" class="gs" display="none" src="data:image/png;base64,""" + kimgs["5"] + """" width="90%">
      specfunc = """
          
      """
      sbutton = """
            <button onclick="showhide('spec')">Spectrum</button>
    """
    else:
      imtab = """
      <div class="boxes" id="s11">
        <img src="data:image/png;base64,""" + cls.seefile(data, cal) + """" width="90%">
        <p>Calibration: """ + str(normal["cal"]) + """, """ + dlist + """
      </div>
      """
      stab = ""
      specfunc = ""
      sbutton = ""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <style>
      	body {
      	background-color: #282828;
      	color: lightgray;
        font-family: mono;
      	}
        .buttons {
          display: flex;
          justify-content: center;
          align-items: center;
        }
        .notebook {
          display: flex;
          align-items:center;
          justify-content: center;
        }
      	.mon {
        	column-count: 2;
        	column-rule: dotted 1px #333;
        	list-style-type: none;
      	}
      	.ctrl {
        	column-count: 2;
        	column-rule: dotted 1px #333;
        	list-style-type: none;
      	}
        .boxes {
            border: 2px solid yellow;
      		  background-color: #383838;
      		  width: 45%;
            margin: 10px;
            padding: 10px;
            display: inline-block;
        }
    </style>
    <script>
      window.onload = function() {
        function getsaved() {
          var stheme = localStorage.getItem("theme");
          var body = document.getElementById("body");
          var boxes = document.getElementsByClassName("boxes");
          if (stheme === "dark") {
              body.style.backgroundColor = "#282828";
              body.style.color = "lightgray";
              body.style.fontFamily = "monospace";
            for (var i = 0; i < boxes.length; i++) {
              boxes[i].style.border = "2px solid yellow";
              boxes[i].style.backgroundColor = "#383838";
            }
          } else if (stheme === "light") {
            body.style.backgroundColor = "white";
            body.style.color = "#282828";
            body.style.fontFamily = "cursive";
            for (var i = 0; i < boxes.length; i++) {
              boxes[i].style.border = "2px solid blue";
              boxes[i].style.backgroundColor = "WhiteSmoke";
            }
          }
          for (var i = 0; i < boxes.length; i++) {
            var thing = boxes[i].id;
            var btheme = localStorage.getItem(thing.concat("sh"));
            if (btheme === "on") {
              boxes[i].style.display = "block";
            } else if (btheme === "off") {
              boxes[i].style.display = "none";
            }
          }
        }
        getsaved();
      }

      """ + specfunc + """
      function showhide(thing) {
          var x = document.getElementById(thing);
          if (x.style.display === "none") {
              x.style.display = "block";
              localStorage.setItem(thing.concat("sh"), "on");
          } else {
              x.style.display = "none";
              localStorage.setItem(thing.concat("sh"), "off");
          }
      }
      function lightswitch() {
        var body = document.getElementById("body");
        var boxes = document.getElementsByClassName("boxes");
        var mode = window.getComputedStyle(body).backgroundColor;
        if (mode === "rgb(40, 40, 40)") {
          body.style.backgroundColor = "white";
          body.style.color = "#282828";
          body.style.fontFamily = "cursive";
          for (var i = 0; i < boxes.length; i++) {
            boxes[i].style.border = "2px solid blue";
            boxes[i].style.backgroundColor = "WhiteSmoke";
          }
          localStorage.setItem("theme", "light");
        } else {
          body.style.backgroundColor = "#282828";
          body.style.color = "lightgray";
          body.style.fontFamily = "mono";
          for (var i = 0; i < boxes.length; i++) {
            boxes[i].style.border = "2px solid yellow";
            boxes[i].style.backgroundColor = "#383838";
          }
          localStorage.setItem("theme", "dark");
        }
      }
      setTimeout(() => location.reload(), 2000);
    </script>
</head>
<body id="body">
    <div class="header">
        <div class="buttons">
            <button onclick="showhide('s11')">S11</button>
            <button onclick="showhide('temps')">Temperature</button>
            """ + sbutton + """
            <button onclick="showhide('tool')">Tools</button>
            <br>
            <button onclick="lightswitch()">Light Switch</button>
        </div>
    </div>
    <div class="notebook">
    """ + stab + """
    """ + imtab + """
    </div>
    <div class="notebook">
    <div class="boxes" id="temps">
      """ + tgraph + """
      """ + terror + """
    </div>
    <div class="boxes" id="tool">
      <h4 style="text-align: center">Motor</h4>
      <div class="mon">
        <li style="text-align:center"><b>AZ</b></li>
        <li>Position: """ + str(mot["az_pos"]) + """</li>
        <li style="text-align:center"><b>EL</b></li>
        <li>Position: """ + str(mot["el_pos"]) + """</li>
      </div>
      <p>Lidar Distance: """ + str(lid["distance_m"]) + """ meters</p>
      <p>Switch State: """ + str(bin(rfs["sw_state"])[2:])[::-1] + """</p>
    </div>
    </div>
</body>
</html>"""
    fiel = ""
    if fname == "":
      fiel = "demo" + str(np.random.randint(1, 1000000)) + ".html"
      fiel = "thisone4986349238648392.html"
    else:
      fiel = cls.ripper(fname) + ".html"
    with open(fiel, "w") as f:
      f.write(html)
      if not cls.opene:
        #subprocess.call(["open", "thisone4986349238648392.html"], shell=True)
        cls.opene = True

  @classmethod
  def check(cls):
    print("Metadata for page: \n" + str(cls.grabbe()))
    print("Temperature: \n" + str(cls.tdata))
  
  @classmethod
  def foldersite(cls, s11folder, path="~/EIGSEP-Flagger"): ## Will evolve.
    opened = False
    for path, folders, files in os.walk(s11folder):
      for fname in files:
        fpath = path + "/" + fname
        data, cal, head, meta = eo.io.read_s11_file(fpath)
        cls.buildpage(meta, data, cal)
        if not opened:
          webbrowser.open(path + "/thisone4986349238648392.html")
          opened = True

#------
w = Website()
spthread = threading.Thread(target=w.seespectrum, args=(Website.ks,), daemon=True)
methread = threading.Thread(target=w.grabbit, args=(), daemon=True)
s11thread = threading.Thread(target=w.grabs11, args=(), daemon=True)
spthread.start()
methread.start()
s11thread.start()
#x=0
#print("Do you want the Chaos? (Type N for no.)")
#y = input()
# if True:#y != "N" and y != "n":
#   THREADS = {"all": threading.Thread(target=w.seespec, args=(True,), daemon=True)}
#   for k in w.ks:
#     THREADS[k] = threading.Thread(target=w.secspec, args=(k,), daemon=True)
#   for k in THREADS:
#     THREADS[k].start()
while True:
    try:
      w.buildpage(active=True)
      #print("Webpage refreshed " + str(x) + " times.")
      #w.check()
      time.sleep(2)
      #x+=1
    except KeyboardInterrupt:
      w.flag = False
      print("Goodbye!!!!!!")
      break
# webthread = threading.Thread(target=refresh, args=())
# webthread.start()
# webthread.join()
