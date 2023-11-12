Websocket Chatroom
 Joseph Nov 14,2022
=========

[Installation]
pip install -r requirements.txt

[Directory layout]
tree /F

├─app.py
├─Readme.txt
├─requirements.txt
│
├─templates/
│      html5_camera.html
│      index.html
│      page.html
│
└─upload/
        20221114-190224.png
        20221114-190431.png


[Run Flask]
python app.py


[Test it]

#chatroom demo
http://127.0.0.1:3000/

#simple return variable
http://127.0.0.1:3000/me

#render template 
it will render templates/page.html with your path name
http://127.0.0.1:3000/hello/AAA
http://127.0.0.1:3000/hello/BBB


#send a camera image (base64)

http://127.0.0.1:3000/video



#Referencs docs
[Flask User’s Guide]
https://flask.palletsprojects.com/en/2.2.x/