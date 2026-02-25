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

class Website: 
  r2 = EigsepRedis(host="10.10.10.10")
  r = EigsepRedis(host="10.10.10.11")
  #r= EigsepRedis(host="192.168.10.83")
  tdata = np.array([[[0],[0]], [[0],[0]], [[0],[0]], [[0],[0]]])
  s11data = {"VNAO": np.array([[0],[0]]), "VNAS": np.array([[0],[0]]), "VNAL": np.array([[0],[0]]),
             "ant": np.array([[0],[0]]), "load": np.array([[0],[0]]), "noise": np.array([[0],[0]]),
             "rec": np.array([[0],[0]])}
  opene = False
  IMGGGG = "uhhhhhhhhhh"
  mlist = [[0], [0], {"A_status": "error", "B_status": "error", "A_timestamp":0, "A_temp":0, "B_timestamp":0, "B_temp":0}, {"A_status": "error", "B_status": "error", "A_timestamp":0, "A_T_now":0, "B_timestamp":0, "B_T_now":0}, {"distance_m": 0}, {"az_pos": 0, "el_pos": 0}, {"sw_state":0}]
  ks = ["0", "02", "04", "1", "13", "15", "2", "24", "3", "35", "4", "5"]
  specgraphs = {}
  running = "1"
  
  spthread = threading.Thread(target=seespectrum, args=(ks,))
  methread = threading.Thread(target=grabbit, args=())
  spthread.start()
  methread.start()

  def __init__(self, hos="10.10.10.11"):
    self.r = EigsepRedis(host=hos)
  
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
    plt.close()
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
    plt.legend(loc="lower right")
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    img64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    return img64

  @classmethod
  def grabbit(cls):
    # global tdata
    # global s11data
    # global r
    meta = cls.r.get_live_metadata()
    tem = meta["temp_mon"]
    tec = meta["tempctrl"]
    cls.tdata = np.append(cls.tdata, [[[tem["A_timestamp"]], [tem["A_temp"]]], [[tem["B_timestamp"]], [tem["B_temp"]]],
                      [[tec["A_timestamp"]], [tec["A_T_now"]]], [[tec["B_timestamp"]], [tec["B_T_now"]]]], axis = 2)
    # ddict = MAGICALGRABBINGFUNCTION()
    #for key in s11data:
    #   if key in ddict:
    #    s11data[key] = np.append(s11data[key], [[timestamp],[point]], axis = 1)
    cls.mlist = [meta["imu_antenna"], meta["imu_panda"], meta["temp_mon"], meta["tempctrl"], meta["lidar"], meta["motor"], meta["rfswitch"]]

  @classmethod
  def grabbe(cls):
    return cls.mlist[0], cls.mlist[1], cls.mlist[2], cls.mlist[3], cls.mlist[4], cls.mlist[5], cls.mlist[6],
    
  @classmethod
  def seetemp(cls):
    plt.figure()
    colors = {"VNAO": "red", "VNAS": "orange", "VNAL": "yellow",
              "ant": "green", "load": "blue", "noise": "purple",
              "rec": "gray"} # Yes, it IS completely necessary to have a different color for each one!
    atm = cls.tdata[0][cls.tdata[0][:, 0].argsort()]
    btm = cls.tdata[1][cls.tdata[1][:, 0].argsort()]
    atc = cls.tdata[2][cls.tdata[2][:, 0].argsort()]
    btc = cls.tdata[3][cls.tdata[3][:, 0].argsort()]
    plt.scatter(atm[0][1:], atm[1][1:], color = "red",label = "A_Temp_Mon")
    plt.scatter(btm[0][1:], btm[1][1:], color = "orange",label = "B_Temp_Mon")
    plt.scatter(atc[0][1:], atc[1][1:], color = "green",label = "A_Temp_Ctrl")
    plt.scatter(btc[0][1:], btc[1][1:], color = "blue",label = "B_Temp_Ctrl")
    plt.title("Temperature")
    plt.legend(loc="lower right")
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    img64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    return img64
  
  @classmethod
  def seespec(cls, k):
    return specgraphs[k]

  @classmethod
  def seespectrum(cls, ks):
    # global IMGGGG
    readspec = r2.read_corr_data(timeout = 3)
    spec = readspec[2]
    for k in ks:
      plt.figure()
      plt.plot(np.log10(np.abs(spec[k])))
      plt.title(str(k) + " " + str(readspec[1]))
      buffer = io.BytesIO()
      plt.savefig(buffer, format='png')
      buffer.seek(0)
      img64 = base64.b64encode(buffer.read()).decode('utf-8')
      cls.specgraphs[k] = img64
      plt.close()
  
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
        mia, mip, tem, tec, lid, mot, rfs = grabbe()
      except KeyError:
        print("No metadata being collected; this is going to cause problems!")
        mia, mip, tem, tec, lid, mot, rfs = [0], [0], {"A_status": "error", "B_status": "error", "A_timestamp":0, "A_temp":0, "B_timestamp":0, "B_temp":0}, {"A_status": "error", "B_status": "error", "A_timestamp":0, "A_T_now":0, "B_timestamp":0, "B_T_now":0}, {"distance_m": 0}, {"az_pos": 0, "el_pos": 0}, {"sw_state":0}
      if len(s11data["VNAO"][:][1]) > 1:
        if len(s11data["rec"][:][1]) > 1:
          normal = activeflag({"rec": s11data["rec"][1:][1]},
                   {"VNAO": s11data["VNAO"][1:][1], "VNAS": s11data["VNAS"][1:][1], "VNAL": s11data["VNAL"][1:][1]})
        else:
          normal = activeflag({"ant": s11data["ant"][1:][1], "load": s11data["load"][1:][1], "noise": s11data["noise"][1:][1]},
                   {"VNAO": s11data["VNAO"][1:][1], "VNAS": s11data["VNAS"][1:][1], "VNAL": s11data["VNAL"][1:][1]})
      else:
        normal = activeflag({"rec": s11data["rec"][:][1]},
                   {"VNAO": s11data["VNAO"][:][1], "VNAS": s11data["VNAS"][:][1], "VNAL": s11data["VNAL"][:][1]})
    else:
      tdata = np.append(tdata, [[[tem["A_timestamp"]], [tem["A_temp"]]], [[tem["B_timestamp"]], [tem["B_temp"]]],
                              [[tec["A_timestamp"]], [tec["A_T_now"]]], [[tec["B_timestamp"]], [tec["B_T_now"]]]], axis = 2)
    tgraph = """
      <img src="data:image/png;base64,""" + seetemp() + """" width="400" height="300">
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
      imtab = """
    <div class="boxes" id="s11">
      <img src="data:image/png;base64,""" + seeactives11() + """" width="400" height="300">
      <p>Calibration: """ + str(normal["cal"]) + """, """ + dlist + """
    </div>
      """
      # stab = ""
      # sbutton = ""
      # specfunc = ""
      # specset = "" alt forwardslash
      stab = """
    <div class="boxes" id="spec">
      <button onclick="showhide('g0')">0</button>
      <button onclick="showhide('g02')">02</button>
      <button onclick="showhide('g04')">04</button>
      <button onclick="showhide('g1')">1</button>
      <button onclick="showhide('g13')">13</button>
      <button onclick="showhide('g15')">15</button>
      <button onclick="showhide('g2')">2</button>
      <button onclick="showhide('g24')">24</button>
      <button onclick="showhide('g3')">3</button>
      <button onclick="showhide('g35')">35</button>
      <button onclick="showhide('g4')">4</button>
      <button onclick="showhide('g5')">5</button>
      <img id="g0" display="none" src="data:image/png;base64,""" + seespec("0") + """" width="400" height="300"> 
      <img id="g02" display="none" src="data:image/png;base64,""" + seespec("02") + """" width="400" height="300"> 
      <img id="g04" display="none" src="data:image/png;base64,""" + seespec("04") + """" width="400" height="300"> 
      <img id="g1" display="block" src="data:image/png;base64,""" + seespec("1") + """" width="400" height="300">
      <img id="g13" display="none" src="data:image/png;base64,""" + seespec("13") + """" width="400" height="300"> 
      <img id="g15" display="none" src="data:image/png;base64,""" + seespec("15") + """" width="400" height="300"> 
      <img id="g2" display="none" src="data:image/png;base64,""" + seespec("2") + """" width="400" height="300"> 
      <img id="g24" display="none" src="data:image/png;base64,""" + seespec("24") + """" width="400" height="300">  
      <img id="g3" display="none" src="data:image/png;base64,""" + seespec("3") + """" width="400" height="300">  
      <img id="g35" display="none" src="data:image/png;base64,""" + seespec("35") + """" width="400" height="300">  
      <img id="g4" display="none" src="data:image/png;base64,""" + seespec("4") + """" width="400" height="300">  
      <img id="g5" display="none" src="data:image/png;base64,""" + seespec("5") + """" width="400" height="300">  
    </div>
    """
      specfunc = """
          
      """
      specset = """
          image.src = "data:image/png;base64,""" + cls.IMGGGG + """";        
    """
      sbutton = """
            <button onclick="showhide('spec')">Spectrum</button>
    """
    else:
      imtab = """
      <div class="boxes" id="s11">
        <img src="data:image/png;base64,""" + seefile(data, cal) + """" width="400" height="300">
        <p>Calibration: """ + str(normal["cal"]) + """, """ + dlist + """
      </div>
      """
      stab = ""
      specfunc = ""
      specset = ""
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
    """ + imtab + """
    <div class="boxes" id="temps">
      """ + tgraph + """
      """ + terror + """
    </div>
    </div>
    <div class="notebook">
    """ + stab + """
    <div class="boxes" id="tool">
      <h4 style="text-align: center">Motor</h4>
      <div class="mon">
        <li style="text-align:center"><b>AZ</b></li>
        <li>Position: """ + str(mot["az_pos"]) + """</li>
        <li style="text-align:center"><b>EL</b></li>
        <li>Position: """ + str(mot["el_pos"]) + """</li>
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
      if not cls.opene:
        #subprocess.call(["open", "thisone4986349238648392.html"], shell=True)
        cls.opene = True

  def foldersite(s11folder, path="~/EIGSEP-Flagger"): ## Will evolve.
    opened = False
    for path, folders, files in os.walk(s11folder):
      for fname in files:
        fpath = path + "/" + fname
        data, cal, head, meta = eo.io.read_s11_file(fpath)
        buildpage(meta, data, cal)
        if not opened:
          webbrowser.open(path + "/thisone4986349238648392.html")
          opened = True

#------
def refresh():
  while True:
    try: 
      Website.buildpage(active=True)
      time.sleep(2)
    except KeyboardInterrupt:
      methread.join()
      specthread.join()
      print("Goodbye!!!!!!")
      break
webthread = threading.Thread(target=refresh, args=())
webthread.start()
webthread.join()
