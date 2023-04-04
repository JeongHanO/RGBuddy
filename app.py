from flask import Flask, render_template, jsonify, request, redirect, url_for
app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.dbjungle

import hashlib, datetime, jwt

KEYCODE = 'RGBuddy_key'

## HTML을 주는 부분
@app.route('/')
def home():
   # return render_template('index.html')
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, KEYCODE, algorithms=['HS256'])
        user_info = db.users.find_one({"id": payload['id']})
        return render_template('calendar.html')
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

@app.route('/login')
def login():
   return render_template('login_.html')

@app.route('/join')
def join():
   return render_template('join.html')

# API 역할을 하는 부분

@app.route('/signup', methods= ['POST'])
def signup():
   id_receive = request.form['id_give']  
   pw_receive = request.form['pw_give']
   name_receive = request.form['name_give']
   team_receive = request.form['team_give']
   phone_receive = request.form['phone_give']

   pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

   user = {'id': id_receive, 'password': pw_hash, 'name' : name_receive, 
            'phone': phone_receive, 'team': team_receive}
   db.users.insert_one(user)

   return jsonify({'result': 'success'})

@app.route('/api/login', methods=['POST', 'GET'])
def api_login():
   id_receive = request.form['id_give']
   pw_receive = request.form['pw_give']
   
   if id_receive is "" or pw_receive is "":
      return jsonify({'result': 'fail', 'msg': '아이디와 비밀번호를 입력하세요.'}) 

   pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

   result = db.users.find_one({'id': id_receive, 'password':pw_hash})

   if result is not None:
      payload = {
         'id': id_receive,
         'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=5)
      }

      token = jwt.encode(payload, KEYCODE, algorithm='HS256')
      return jsonify({'result': 'success', 'token':token})
   else:
      return jsonify({'result': 'fail', 'msg': '아이디 또는 비밀번호가 일치하지 않습니다.'}) 




if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)