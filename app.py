
from flask import Flask, render_template, jsonify, request, redirect, url_for
app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.dbjungle

import hashlib, jwt, calendar
from datetime import datetime, timedelta

KEYCODE = 'RGBuddy_key'

def tokenCheck():
   token_receive = request.cookies.get('mytoken')
   try:
      payload = jwt.decode(token_receive, KEYCODE, algorithms=['HS256'])
      user_info = db.users.find_one({"id": payload['id']})
   except jwt.ExpiredSignatureError:
      return [False, redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))]
   except jwt.exceptions.DecodeError:
      return [False, redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))]
   return [ True, user_info]



## HTML을 주는 부분
@app.route('/')
def home():
   login = tokenCheck()
   if login[0]==True:
      return render_template('index.html')
   else:
      return login[1]

@app.route('/login')
def login():   
   login = tokenCheck()
   if login[0]==True:
      return redirect(url_for("calendar", msg="로그인 되어있습니다."))
   else:
      return render_template('login.html')

@app.route('/signup')
def signup():   
   login = tokenCheck()
   if login[0]==True:
      return redirect(url_for("calendar", msg="로그인 되어있습니다."))
   else:
      return render_template('join.html')



@app.route('/calendar')
def calendar():
    #(추가필요) 로그인이 되어있는지 확인해야 함. 
   login = tokenCheck()
   if login[0]==True:
      now = datetime.now()
      year = now.year
      month = now.month
      day = now.day
      weekday = now.weekday()

      weekrange=[]
      for i in range(14):
         weekrange.append((now-timedelta(days=weekday-i)).day)
      return render_template('calendar_.html', month=month, day=day, weekday=weekday, weekrange=weekrange)
   else:
      return login[1]


@app.route('/matching', methods = ['GET'])
def matching():

   login = tokenCheck()
   if login[0]==True:
      teamColor = login[1]['team']
    
      date = request.args.get('date')

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
   else:
      return login[1]

@app.route('/matchLog')
def matchLog():
   login = tokenCheck()
   if login[0]==True:
      userInfo = login[1]
      
      userInfo['id']
      return render_template('matchLog.html', userName=userInfo['name'], waitDates=['4/8', '4/15'])
      
   else:
      return login[1]

# API 역할을 하는 부분

@app.route('/api/signup', methods= ['POST'])
def api_signup():
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
         'exp': datetime.utcnow() + timedelta(minutes=5)
      }

      token = jwt.encode(payload, KEYCODE, algorithm='HS256')
      return jsonify({'result': 'success', 'token':token})
   else:
      return jsonify({'result': 'fail', 'msg': '아이디 또는 비밀번호가 일치하지 않습니다.'}) 

@app.route('/api/apply', methods= ['POST'])
def apply():

    login = tokenCheck()
    if login[0]==True:
        userInfo = login[1]
    else:
        return login[1]
    
    date_receive = request.form['date_give']
    month, day = map(str, date_receive.split(" "))
    month ='January'
    enMonth = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December' ]
    month_number = enMonth.index(month)
    date_formatted = str(month_number)+'/'+str(day)

    teamColor = userInfo['team']
    userId = userInfo['id']
    
   #  query = {"date": date_formatted}
   #  new_value = {"$push": {teamColor: userId}}
    # 데이터 업데이트
   #  db.dates.update_one(query, new_value)

    date_col=db.dates.find_one({'date':date_formatted})
    date_col.update  


    return jsonify({'result': 'success'})


if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)

