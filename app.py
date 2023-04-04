
from flask import Flask, render_template, jsonify, request, redirect, url_for
app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.dbjungle

import hashlib, jwt, calendar
from datetime import datetime

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

@app.route('/calendar')
def calendar():
    #(추가필요) 로그인이 되어있는지 확인해야 함.
    now = datetime.now()
    year = now.year
    month = now.month
    day = now.day
    weekday = now.weekday()
    
    return render_template('calendar.html', year=year, month=month, day=day, weekday=weekday)
    
#GET으로 날짜값을 넘겨준다음, 그 날짜에 해당하는 
@app.route('/matching', methods = ['GET'])
def matching():

    #(추가필요) 로그인이 되어있는지 확인해야 함.
    
    #(수정필요) 사용자의 팀을 불러서 저장
    teamColor ='red' # 임시저장
    
    
    date = request.args.get('date')
    
    #받아온 date로 db에서 각 팀에 저장된 사람의 수를 불러옴
    query = {'date': date}
    
    data = list(db.dates.find(query))
    
    if not data:
        redCount = 0
        blueCount = 0
        greenCount=0
    else:
        redCount = len(data[0]['red'])
        blueCount = len(data[0]['blue'])
        greenCount = len(data[0]['green'])
    
    enMonth = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December' ]
    month, day = map(int, date.split("/"))
    enDate = enMonth[month]+" "+str(day)
   

    return render_template('matching.html', redCount=redCount, blueCount=blueCount, greenCount=greenCount, teamColor=teamColor, date=enDate)


if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)

