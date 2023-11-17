from flask import *  
from flask_socketio import SocketIO, emit
import base64
import datetime
import json
import pandas as pd 
from aimodel import AI_model #joseph
import os 

from EDA_carrefour import * 

app = Flask(__name__,static_folder='web')

# http://127.0.0.1:3000

@app.route('/')
def index():
   #return render_template('index.html')
   return app.send_static_file('index.html')
    
    
@app.route('/hello/<name>')
def hello(name):
    return render_template('page.html', name=name)
    
@app.route('/video')
def goto_camera():
    return render_template('html5_camera.html')
    
    
@app.route('/item')
def goto_item():
    return render_template('list_item.html')

@app.route('/analysis')
def goto_analysis():
    return render_template('data_analysis.html')  
    
@app.route('/upload')
def upload_file():
    return render_template('file_upload_form.html')  
    
def get_current_user():
    return {'name':'joseph','password':'1234'}
    
@app.route("/me")
def me_api():
    user = get_current_user()
    print(user)
    return {
        "username": user['name'],
        "password": user['password']
    }

#-------------websocket------------------------    
socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*")


def save_img(msg):

    filename=datetime.datetime.now().strftime("%Y%m%d-%H%M%S")+'.png'
    base64_img_bytes = msg.encode('utf-8')
    with open('./web/upload/'+filename, "wb") as save_file:
        save_file.write(base64.decodebytes(base64_img_bytes))


#user defined event 'client_event'
@socketio.on('client_event')
def client_msg(msg):
    print('received from client:',msg['data'])
    emit('server_response', {'data': msg['data']}, broadcast=False) #include_self=False

#user defined event 'connect_event'
@socketio.on('connect_event')   
def connected_msg(msg):
    print('received connect_event')
    emit('server_response', {'data': msg['data']})
    
    
#user defined event 'capture_event'
@socketio.on('capture_event')   
def connected_msg(msg):
    print('received capture_event')
    #print(msg)
    save_img(msg)
    #here we just send back the original image to browser.
    #maybe, you can do image processinges before sending back 
    emit('capture_event', msg, broadcast=False)
    

    
#------SQLite stuff-----------------

from sqlite_utils import *


@socketio.on('topK_sales')   
def  trigger_topK_sales(msg):
    print('topK_sales event')
    k=msg
    print(msg)
   
    print(f'----------銷售額前 {k}名的商品-----------------')
    top_K_prod=get_top_k_product(train_df,k,'total_sales')
    for i in top_K_prod: print(i)
    
    emit('topK_sales', {'data': top_K_prod}, broadcast=False)
    
    
@socketio.on('get_customer_purchase_info')   
def  trigger_topK_sales(msg):
    print('get_customer_purchase_info event')
    data=ananyze_customer_amount(train_df).to_json(orient='records')
    print(data)
    emit('get_customer_purchase_info', {'data': data}, broadcast=False)
     


@socketio.on('get_allitem_event')   
def  trigger_allitem_item(msg):
     print('trigger_allitem_item')
     newitems=query_db_json(db,select_sql)
     emit('new_item_event', {'data': newitems }, broadcast=False)
     

@socketio.on('new_item_event')   
def  trigger_new_item(msg):
     print('trigger new_item')
     newitems=[{'pid':'1234','p_name':'拿鐵咖啡','p_price':50},
              {'pid':'1235','p_name':'焦糖咖啡','p_price':80}]
     newitems=json.dumps(newitems)
     emit('new_item_event', {'data': newitems }, broadcast=False)

@app.route('/upload', methods = ['POST','GET'])  
def success():  
    if request.method == 'POST':  
        f = request.files['file']  
        f.save('web/upload/'+f.filename)  
        
        #predict the image 
        img_file=os.path.join('web/upload',f.filename)
        prob,label=model.predict(img_file)

        print('Class:', label, end='')
        print('Confidence score:', prob)
     
        return render_template("success.html", name = img_file,class_name=label,confidence=prob)  

def init_gpu():
    #----allocate more GPU memory if it needed--------
    import tensorflow as tf
    config = tf.compat.v1.ConfigProto(gpu_options = 
                         tf.compat.v1.GPUOptions(per_process_gpu_memory_fraction=0.8))
    # device_count = {'GPU': 1}
        
    config.gpu_options.allow_growth = True
    session = tf.compat.v1.Session(config=config)
    tf.compat.v1.keras.backend.set_session(session)
    
if __name__ == '__main__':
    
    init_gpu() 

    model_dir='model'
    model_file='keras_Model.h5'
    label_file='labels.txt'

    model_file=os.path.join(model_dir,model_file)
    class_file=os.path.join(model_dir,label_file)
    model=AI_model(model_file,class_file)
    

    socketio.run(app, debug=True, host='0.0.0.0', port=3000)
 
