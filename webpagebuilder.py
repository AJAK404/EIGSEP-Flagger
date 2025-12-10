import webbrowser
import io
import base64
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import eigsep_observing as eo
from ActiveFlagger import activeflag
from eo import EigsepRedis

r = EigsepRedis(host="10.10.10.11")
tdata = np.array([[[0],[0]], [[0],[0]], [[0],[0]], [[0],[0]]])
s11data = {"VNAO": np.array([[0],[0]]), "VNAS": np.array([[0],[0]]), "VNAL": np.array([[0],[0]]),
           "ant": np.array([[0],[0]]), "load": np.array([[0],[0]]), "noise": np.array([[0],[0]]),
           "rec": np.array([[0],[0]])}

def lin(x):
  return 20* np.log10(np.abs(x))

def seefile(data, cal):
  plt.figure()
  colors = {"VNAO": "red", "VNAS": "orange", "VNAL": "yellow",
            "ant": "green", "load": "blue", "noise": "purple",
            "rec": "gray"} # Yes, it IS completely necessary to have a different color for each one!
  for yap in colors:
    if yap[:3] == "VNA":
      plt.plot(lin(cal[yap]), color = colors[yap],label = yap)
    else:
      if len(data) == 1 and yap == "rec":
        plt.plot(lin(data[yap]), color = colors[yap],label = yap)
      elif len(data) == 3 and yap != "rec":
        plt.plot(lin(data[yap]), color = colors[yap],label = yap)
  plt.title("S11")
  plt.legend()
  buffer = io.BytesIO()
  plt.savefig(buffer, format='png')
  buffer.seek(0)
  img64 = base64.b64encode(buffer.read()).decode('utf-8')
  return img64
  
def seeactives11():
  plt.figure()
  colors = {"VNAO": "red", "VNAS": "orange", "VNAL": "yellow",
            "ant": "green", "load": "blue", "noise": "purple",
            "rec": "gray"} # Yes, it IS completely necessary to have a different color for each one!
  plt.title("S11")
  for yap in colors:
    if len(s11data[yap]) > 1:
      plt.scatter(s11data[yap][0][1:], s11data[yap][1][1:], color = colors[yap], label = yap)
  plt.legend()
  buffer = io.BytesIO()
  plt.savefig(buffer, format='png')
  buffer.seek(0)
  img64 = base64.b64encode(buffer.read()).decode('utf-8')
  return img64
  
def grabbit():
  global tdata
  global s11data
  global r
  meta = r.get_live_metadata()
  dta = r.read_vna_data()
  tem = meta["temp_mon"]
  tec = meta["tempctrl"]
  tdata = np.append(tdata, [[[tem["A_timestamp"]], [tem["A_temp"]]], [[tem["B_timestamp"]], [tem["B_temp"]]],
                    [[tec["A_timestamp"]], [tec["A_T_now"]]], [[tec["B_timestamp"]], [tec["B_T_now"]]]], axis = 2)
  
def seetemp():
  global tdata
  plt.figure()
  colors = {"VNAO": "red", "VNAS": "orange", "VNAL": "yellow",
            "ant": "green", "load": "blue", "noise": "purple",
            "rec": "gray"} # Yes, it IS completely necessary to have a different color for each one!
  atm = tdata[0][tdata[0][:, 0].argsort()]
  btm = tdata[1][tdata[1][:, 0].argsort()]
  atc = tdata[2][tdata[2][:, 0].argsort()]
  btc = tdata[3][tdata[3][:, 0].argsort()]
  plt.scatter(atm[0][1:], atm[1][1:], color = "red",label = "A_Temp_Mon")
  plt.scatter(btm[0][1:], btm[1][1:], color = "orange",label = "B_Temp_Mon")
  plt.scatter(atc[0][1:], atc[1][1:], color = "green",label = "A_Temp_Ctrl")
  plt.scatter(btc[0][1:], btc[1][1:], color = "blue",label = "B_Temp_Ctrl")
  plt.title("Temperature")
  plt.legend()
  buffer = io.BytesIO()
  plt.savefig(buffer, format='png')
  buffer.seek(0)
  img64 = base64.b64encode(buffer.read()).decode('utf-8')
  return img64

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

def buildpage(meta, data, cal, spec = {}, fname="", active=False):
  normal = activeflag(data,cal)
  mia = meta["imu_antenna"]
  mip = meta["imu_panda"]
  tem = meta["temp_mon"]
  tec = meta["tempctrl"]
  lid = meta["lidar"]
  mot = meta["motor"]
  rfs = meta["rfswitch"]
  if active:
    grabbit()
  else:
    tdata = np.append(tdata, [[[tem["A_timestamp"]], [tem["A_temp"]]], [[tem["B_timestamp"]], [tem["B_temp"]]],
                            [[tec["A_timestamp"]], [tec["A_T_now"]]], [[tec["B_timestamp"]], [tec["B_T_now"]]]], axis = 2)
  tgraph = """
      <img src="data:image/png;base64,""" + seetemp() + """" width="400" height="300">
      """
  terror = """"""
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
    imtab = """
    <div class="boxes" id="s11">
      <img src="data:image/png;base64,""" + seeactives11() + """" width="400" height="300">
      <p>Calibration: """ + str(normal["cal"]) + """, """ + dlist + """
    </div>
      """
  else:
    imtab = """
    <div class="boxes" id="s11">
      <img src="data:image/png;base64,""" + seefile(data, cal) + """" width="400" height="300">
      <p>Calibration: """ + str(normal["cal"]) + """, """ + dlist + """
    </div>
      """
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
      		  width: 800px;
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
            var thing = boxes[i].id
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
            <button onclick="showhide('tool')">Tools</button>
            <br>
            <button onclick="lightswitch()">Light Switch</button>
        </div>
    </div>
    <div class="notebook">
    """ + imtab + """
    <div class="boxes" id="temps">
      """ + tgraph + """
      """ + terror + """
    </div>
    </div>
    <div class="notebook">
    <div class="boxes" id="tool">
      <h4 style="text-align: center">Motor</h4>
      <div class="mon">
        <li style="text-align:center"><b>AZ</b></li>
        <li>Position: """ + str(mot["az_pos"]) + """</li>
        <li>Direction: """ + str(mot["az_dir"]) + """</li>
        <li>Remaining Steps: """ + str(mot["az_remaining_steps"]) + """</li>
        <li>Maximum Pulses: """ + str(mot["az_max_pulses"]) + """</li>
        <li style="text-align:center"><b>EL</b></li>
        <li>Position: """ + str(mot["el_pos"]) + """</li>
        <li>Direction: """ + str(mot["el_dir"]) + """</li>
        <li>Remaining Steps: """ + str(mot["el_remaining_steps"]) + """</li>
        <li>Maximum Pulses: """ + str(mot["el_max_pulses"]) + """</li>
      </div>
      <p>Lidar Distance: """ + str(lid["distance_m"]) + """ meters</p>
      <p>Switch State: """ + str(bin(rfs["sw_state"]))[::-1] + """</p>
    </div>
    </div>
</body>
</html>"""
  fiel = ""
  if fname == "":
    fiel = "demo" + str(np.random.randint(1, 1000000)) + ".html"
    fiel = "thisone4986349238648392.html"
  else:
    fiel = ripper(fname) + ".html"
  with open(fiel, "w") as f:
    f.write(html)

def foldersite(s11folder, path="."): ## Will evolve.
  opened = False
  for path, folders, files in os.walk(s11folder):
    for fname in files:
      fpath = path + "/" + fname
      data, cal, head, meta = eo.io.read_s11_file(fpath)
      buildpage(meta, data, cal)
      if not opened:
        webbrowser.open(path + "/thisone4986349238648392.html")
        opened = True
foldersite("./july2025_S11")
