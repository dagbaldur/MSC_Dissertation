# [START gae_python38_app]
# [START gae_python3_app]
from flask import Flask,render_template,request
#misc libraries
import base64 #needed to decode msgs
import json
import os
import pandas as pd
import numpy as np
import plotly
import plotly.express as px
import datetime

#google libraries
from google.cloud import pubsub_v1
from google.oauth2 import id_token
from google.auth.transport import requests
#from google.cloud import iot_v1

#created libraries
from iot_controller import devices
from data_controller import IoT_Data
from storage_controller import Storage_Central

app = Flask(__name__)
#inicialization of app, importing dash for the plots/dashboard
#def init_app():
#    app = Flask(__name__)
#    with app.app_context():
#        from plotlydash.dashboard import create_dashboard
#        app = create_dashboard(app)
#        return app



#inicialization of env. variables - enables handling of the messages from trusted sources
#also sets the topic(s) to use for the cloud app
#NOTE: the variables are environment variables which must be created before deploying the application
#app.config['GOOGLE_CLOUD_PROJECT'] = os.environ['GOOGLE_CLOUD_PROJECT']
#app.config['PUBSUB_VERIFICATION_TOKEN'] = os.environ['PUBSUB_VERIFICATION_TOKEN']
#app.config['PUBSUB_TOPIC'] = os.environ['PUBSUB_TOPIC']

#Some additional variables required for the app per instance
MESSAGES = []
TOKENS = []
edge = devices()
idata = IoT_Data()
imagec = Storage_Central()


@app.route('/')
def main():
    df = idata.getAnalytics(edge.list_registires())

    #prepare some tags for data search
    registries = df['registry'].unique()
    devices = df['device'].unique()
    
    
    fig = px.bar(df,x='device',y='count',color='crack',barmode='group',title="Detections on devices")
    dev_graph = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)
    
    fig = px.bar(df,x='registry',y='count',color='crack',barmode='group',title="Detections on registries")
    reg_graph = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)

    range_end = datetime.date.today()
    range_start = range_end - datetime.timedelta(days=3)
    
    date_summary = df[df['crack'] == True].groupby(['time']).agg('count').drop(['device','filename','registry','confidence','crack'],axis=1).reset_index()
    print(date_summary)

    fig = px.line(date_summary,x='time',y='count',hover_data={'time':"|%B %d %Y, %H:%M"},range_x=[str(range_start),str(range_end)],title="Cracks detected (T-3 days)")
    date_graph = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)

    stats = df.describe().to_html(table_id="statistics")
    df_table = df.to_html(table_id='full_ds')

    return render_template("Analytics.html",full_tb=df_table,statTable=stats,regGraph=reg_graph,devGraph=dev_graph,dateGraph=date_graph)

@app.route('/callback',methods=['POST','GET'])
def cb():
    return gm(request.args.get('data'))

def gm(test='123'):
    #fig = px.line([1,2,3],x='123')
    #graphJSON = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)
    #return graphJSON
    return test

@app.route('/deviceStates')
def getDeviceStatus():
    list_devices = edge.device_states()
    return list_devices

@app.route('/image',methods=['GET'])
def getImage():
    img = request.args.get('imageName')
    imgs = imagec.getImage(img)
    if imgs is not None:
        dict_image = {"image":imgs}
        return json.dumps(dict_image)
        #return render_template("render_image.html",image=imgs)
    else:
        return error("Image not found")

@app.route("/queryImage",methods=['GET'])
def queryImage():
    query = request.args.get('query')
    value = request.args.get('value')
    results = {}
    if query == 'date':
        lower = value.split("|")[0]
        upper = value.split("|")[1]
        results = idata.getByDate(lower,upper,limit=99)
    elif query == 'registry':
        results = idata.getAllByRegistry(value,limit=99)
    elif query == "device":
        results = idata.getAllByDevice(value,limit=99)

    json_imgs = pd.DataFrame(list(map(lambda x: x.to_dict(),results))).to_json(orient="index")
    
    return json_imgs

@app.route('/device')
def getDeviceState():
    df = None
    df_table = None
    images = None
    registry = request.args.get('registryId')
    device = request.args.get('deviceId')
    edge.set_registry(registry)
    dv = edge.set_device(device)

    if dv is not None:
        dev_info = edge.get_device_info(device)

        if len(dev_info) > 0:
            df = idata.getAnalyticsDevice(device)
            if type(df) is not type(None):
                df_table = df.sort_values(by=['time'],ascending=False).drop(['registry','count','device'],axis=1).to_html(table_id='ds_device',classes=["hover","table-striped","table-bordered"])
                images = df.sort_values(by=['time'],ascending=False)[0:16].drop(['registry','count','device','confidence'],axis=1).to_json(orient="index")
                images = json.dumps(images)
            print(dev_info)
        return render_template("Devices.html",registry=registry,device=json.dumps(dev_info),ds_imgs=df_table,img_list=images)            
    else:
        return error("Device not found")

@app.route('/listDevs')
def renderDevices():
    return render_template('RegistryCards.html')

@app.route('/command', methods=['POST'])
def sendCommand():    
    reg = request.form.get('RegistryID')
    dev = request.form.get('DeviceID')
    msg = request.form.get('Command')
    print(reg)
    print(dev)
    response = { "Response" : edge.send_command(reg,dev,msg) }
    print(response)
    return json.dumps(response)

@app.route('/devices')
def getDevices():
    registry = request.args.get('Registry')
    if registry != None:
        edge.set_registry(registry)
    devices = edge.list_devices()
    return devices

@app.route('/registries')
def getRegistries():
    registries = edge.list_registires()
    return registries

@app.route('/tracking')
def getTracking():
    return "Tracking section"

@app.route('/imageList',methods=['GET'])
def images():
    
    return render_template("Images.html")

@app.route('/imgs')
def getImageList():
    tst = idata.getAllByDevice('Device2')
    return str(len(tst))

@app.errorhandler(500)
def error(e):
    return f"Ooops...gotta er...fix that...{e}"

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python3_app]
# [END gae_python38_app]