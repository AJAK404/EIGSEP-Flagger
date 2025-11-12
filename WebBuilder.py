import matplotlib.pyplot as plt
import numpy
from ActiveFlagger.py import activeflag()

def buildpage(meta, fname="", image="", normal = {}):
  mia = meta["imu_antenna"]
  mip = meta["imu_panda"]
  tem = meta["temp_mon"]
  tec = meta["tempctrl"]
  lid = meta["lidar"]
  mot = meta["motor"]
  rfs = meta["rfswitch"]
  if image == "":
    imtab = ""
    imbut = ""
  else:
    if len(normal) == 2:
      dlist = """
      <p>Recording: """ + str(normal["rec"]) + """</p>
      """
    else:
      dlist = """
      <p>Antenna: """ + str(normal["ant"]) + """</p>
      <p>Load: """ + str(normal["load"]) + """</p>
      <p>Noise: """ + str(normal["noise"]) + """</p>
      """
    imtab = """
    <div class="boxes" id="s11">
    	<h3 style="text-align: center">S11</h3>
      <img src="/content/plot.png">
      <h4 style="text-align: center">Is Normal?</h4>
      <p>Calibration: """ + str(normal["cal"]) + """</p>
      """ + dlist + """
    </div>
      """
    imbut = """
            <button onclick="showhide('s11')">S11</button>

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
          display: grid;
          place-items: center;
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
      function showhide(thing) {
          var x = document.getElementById(thing);
          if (x.style.display === "none") {
              x.style.display = "block";
          } else {
              x.style.display = "none";
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
        } else {
          body.style.backgroundColor = "#282828";
          body.style.color = "lightgray";
          body.style.fontFamily = "mono";
          for (var i = 0; i < boxes.length; i++) {
            boxes[i].style.border = "2px solid yellow";
            boxes[i].style.backgroundColor = "#383838";
          }
        }
      }
    </script>
</head>
<body id="body">
    <div class="header">
        <h1 style="text-align: center;">Metadata<br>""" + fname[-25:-3] + """</h1>
        <div class="buttons">
            """ + imbut + """
            <button onclick="showhide('antenna')">Antenna</button>
            <button onclick="showhide('panda')">Panda</button>
            <button onclick="showhide('temps')">Temperature</button>
            <button onclick="showhide('tool')">Tools</button>
            <br>
            <button onclick="lightswitch()">Light Switch</button>
        </div>
    </div>
    <div class="notebook">
    """ + imtab + """
    <div class="boxes" id="antenna">
    	<h3 style="text-align: center">Antenna</h3>
    	<p>Status: """ + str(mia["status"]) + """</p>
      	<p>App: """ + str(mia["app_id"]) + """</p>
      	<p>Quaternion: """ + str(mia["quat_real"]) + """ + """ + str(mia["quat_i"]) + """ <b>i</b> + """ + str(mia["quat_j"]) + """ <b>j</b> + """ + str(mia["quat_k"]) + """ <b>k</b></p>
        <p>Acceleration: (""" + str(mia["accel_x"]) + """, """ + str(mia["accel_y"]) + """, """ + str(mia["accel_z"]) + """)</p>
      	<p>Linear Acceleration: (""" + str(mia["lin_accel_x"]) + """, """ + str(mia["lin_accel_y"]) + """, """ + str(mia["accel_z"]) + """)</p>
      	<p>Gyroscope: (""" + str(mia["gyro_x"]) + """, """ + str(mia["gyro_y"]) + """, """ + str(mia["gyro_z"]) + """)</p>
      	<p>Magnet: (""" + str(mia["mag_x"]) + """, """ + str(mia["mag_y"]) + """, """ + str(mia["mag_z"]) + """)</p>
      	<p>Calibrated: """ + str(mia["calibrated"]) + """</p>
      	<p>Acceleration Calibration: """ + str(mia["accel_cal"]) + """</p>
      	<p>Magnet Calibration: """ + str(mia["mag_cal"]) + """</p>
    </div>
    <div class="boxes" id="panda">
      <h3 style="text-align: center">Panda</h3>
    	<p>Status: """ + str(mip["status"]) + """</p>
      	<p>App: """ + str(mip["app_id"]) + """</p>
      	<p>Quaternion: """ + str(mip["quat_real"]) + """ + """ + str(mip["quat_i"]) + """ <b>i</b> + """ + str(mip["quat_j"]) + """ <b>j</b> + """ + str(mip["quat_k"]) + """ <b>k</b></p>
        <p>Acceleration: (""" + str(mip["accel_x"]) + """, """ + str(mip["accel_y"]) + """, """ + str(mip["accel_z"]) + """)</p>
      	<p>Linear Acceleration: (""" + str(mip["lin_accel_x"]) + """, """ + str(mip["lin_accel_y"]) + """, """ + str(mip["accel_z"]) + """)</p>
      	<p>Gyroscope: (""" + str(mip["gyro_x"]) + """, """ + str(mip["gyro_y"]) + """, """ + str(mip["gyro_z"]) + """)</p>
      	<p>Magnet: (""" + str(mip["mag_x"]) + """, """ + str(mip["mag_y"]) + """, """ + str(mip["mag_z"]) + """)</p>
      	<p>Calibrated: """ + str(mip["calibrated"]) + """</p>
      	<p>Acceleration Calibration: """ + str(mip["accel_cal"]) + """</p>
      	<p>Magnet Calibration: """ + str(mip["mag_cal"]) + """</p>
    </div>
    <div class="boxes" id="temps">
      <h3 style="text-align: center">Temperature</h3>
      <h4 style="text-align: center">Monitoring</h4>
       <div class="mon">
         	<li style="text-align:center"><b>A</b></li>
      		<li>Status: """ + str(tem["A_status"]) + """</li>
         	<li>Temperature: """ + str(tem["A_temp"]) + """</li>
         	<li>Timestamp: """ + str(tem["A_timestamp"]) + """</li>
         	<li style="text-align:center"><b>B</b></li>
         	<li>Status: """ + str(tem["B_status"]) + """</li>
         	<li>Temperature: """ + str(tem["B_temp"]) + """</li>
         	<li>Timestamp: """ + str(tem["B_timestamp"]) + """</li>
      </div>
      <p>App: """ + str(tem["app_id"]) + """</p>
      <h4 style="text-align: center">Control</h4>
      <div class="ctrl">
        	<li style="text-align:center"><b>A</b></li>
      		<li>Status: """ + str(tec["A_status"]) + """</li>
        	<li>Current Temperature: """ + str(tec["A_T_now"]) + """</li>
        	<li>Timestamp: """ + str(tec["A_timestamp"]) + """</li>
        	<li>Target: """ + str(tec["A_T_target"]) + """</li>
        	<li>Drive Level: """ + str(tec["A_drive_level"]) + """</li>
        	<li>Enabled: """ + str(tec["A_enabled"]) + """</li>
        	<li>Active: """ + str(tec["A_active"]) + """</li>
        	<li>Intentionally Disabled: """ + str(tec["A_int_disabled"]) + """</li>
        	<li>Hysteresis: """ + str(tec["A_hysteresis"]) + """</li>
        	<li style="text-align:center"><b>B</b></li>
      		<li>Status: """ + str(tec["B_status"]) + """</li>
        	<li>Current Temperature: """ + str(tec["B_T_now"]) + """</li>
        	<li>Timestamp: """ + str(tec["B_timestamp"]) + """</li>
        	<li>Target: """ + str(tec["B_T_target"]) + """</li>
        	<li>Drive Level: """ + str(tec["B_drive_level"]) + """</li>
        	<li>Enabled: """ + str(tec["B_enabled"]) + """</li>
        	<li>Active: """ + str(tec["B_active"]) + """</li>
        	<li>Intentionally Disabled: """ + str(tec["B_int_disabled"]) + """</li>
        	<li>Hysteresis: """ + str(tec["B_hysteresis"]) + """</li>
      </div>
      <p>App: """ + str(tec["app_id"]) + """</p>
    </div>
    <div class="boxes" id="tool">
      <h3 style="text-align: center">Tools</h3>
      <h4 style="text-align: center">Lidar</h4>
      <p>Status: """ + str(lid["status"]) + """</p>
      <p>App: """ + str(lid["app_id"]) + """</p>
      <p>Distance: """ + str(lid["distance_m"]) + """ meters</p>
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
      <p>Status: """ + str(mot["status"]) + """</p>
      <p>App: """ + str(mot["app_id"]) + """</p>
      <h4 style="text-align: center">Switch</h4>
      <p>Status: """ + str(rfs["status"]) + """</p>
      <p>App: """ + str(rfs["app_id"]) + """</p>
      <p>State: """ + str(rfs["sw_state"]) + """</p>
    </div>
    </div>
</body>
</html>"""
  fiel = ""
  if fname == "":
    fiel = "demo" + str(np.random.randint(1, 1000000)) + ".html"
    fie = "thisone.html"
  else:
    fiel = ripper(fname) + ".html"
  with open(fiel, "w") as f:
    f.write(html)
  print(fiel)
  IPython.display.HTML(filename = fiel)

def seefile(fname):
  data, cal, head, meta = eo.io.read_s11_file(fname)
  fn = ripper(fname)
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
  titl = fn
  plt.title(titl)
  plt.legend()
  plt.savefig("plot.png")
  buildpage(meta, fn, "plot.png", activeflag(data, cal))

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

seefile("/content/july2025_S11/ants11_20250719_110031.h5")
