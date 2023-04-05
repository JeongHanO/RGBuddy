
from flask import Flask, render_template, jsonify, request, redirect, url_for
app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.dbjungle

import hashlib, jwt, calendar, random
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

def rand_res():
   # collection =db['restaurants']
   data = list(db.restaurants.find())
   random_data = random.sample(data, 2)
   return [random_data[0]['name'],random_data[1]['name']]

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

@app.route('/join')
def join():   
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

@app.route('/matchLog', methods = {'GET'})
def matchLog():
   login = tokenCheck()
   if login[0]==True:
      userInfo = login[1]

      dates = userInfo['date']
      not_matched=[]
      matched=[]
      print(dates)
      
      for date in dates:
         data = db.dates.find_one({'date': date})
         index = data[userInfo['team']].index(userInfo['id'])
         print(index)
         if min(len(data['red']), len(data['green']), len(data['blue'])) < index+1 :
            #매칭 되지 않은 날짜
            not_matched.append(date)
         else:
            #매칭 된 날짜
            suc_date = [date]
            for team in ['red', 'green','blue']:
               id=data[team][index]
               phone=db.users.find_one({'id': data['red'][index]})['phone']
               suc_date.append([id, phone])
            suc_date.append(rand_res())
            matched.append(suc_date)

                  

      return render_template('matchLog.html', userName=userInfo['name'], not_matched=not_matched, matched=matched)
      
   else:
      return login[1]

# API 역할을 하는 부분
@app.route('/api/idcheck', methods = ['POST'])
def api_idCheck():
   id_receive = request.form['id_give']
   check=db.users.find_one({'id': id_receive})
   if check is None:
      return jsonify({'result':'success'})
   else:
      return jsonify({'result':'fail','msg':'이미 존재하는 아이디입니다!'})
   
@app.route('/signup', methods= ['POST','GET'])
def api_signup():
   id_receive = request.form['id_give']  
   pw_receive = request.form['pw_give']
   name_receive = request.form['name_give']
   team_receive = request.form['team_give']
   phone_receive = request.form['phone_give']

   pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

   user = {'id': id_receive, 'password': pw_hash, 'name' : name_receive, 
            'phone': phone_receive, 'team': team_receive, 'date':[]}
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

@app.route('/api/apply', methods= ['POST','GET'])
def api_apply():

    login = tokenCheck()
    if login[0]==True:
        userInfo = login[1]
    else:
        return login[1]
    
    date_receive = request.form['date_give']
    month, day = map(str, date_receive.split(" "))
    enMonth = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December' ]
    month_number = enMonth.index(month)
    date_formatted = str(month_number)+'/'+str(day)

    if date_formatted in userInfo['date']:
      return jsonify({'result': 'exist'})


    teamColor = userInfo['team']
    userId = userInfo['id']
   
    newDate = userInfo['date']+[date_formatted]
    db.users.update_one({'id': userId},{"$set":{'date':newDate}})

    data = db.dates.find_one({'date': date_formatted})
    print(data)
    if data is not None:
       print('date db found')
       new_list = data[teamColor]+[userId]
       print(new_list)
       db.dates.update_one({'date':date_formatted},{"$set": {teamColor: new_list}})
       
    else:
       print('no date db')
       db_date = {'date': date_formatted, 'red': [], 'green': [], 'blue': []}
       db_date[teamColor].append(userId)
       db.dates.insert_one(db_date)

    return jsonify({'result': 'success'})


@app.route('/api/cancel', methods=['POST'])
def api_cancel():
   login = tokenCheck()
   if login[0] == True:
      userInfo = login[1]
   else:
      return login[1]
   
   #날짜값 필요, 계정 아이디 필요
   userId = userInfo['id']
   date_receive = request.form['date_give']  # 4/11 형식으로 받아옴
   
   #userdate 리스트를 불러와서
   userDates = userInfo['date'] 


   #userDates 안에 date_receive랑 같으면 지워줌
   if date_receive in userDates:
      userDates.remove(date_receive)
   db.users.update_one({'id': userId}, {
                          "$set": {'date': userDates}})
   teamColor = userInfo['team'] ## 팀칼라에 유저의 팀 정보를 저장

   query = {'date': date_receive}
   data = db.dates.find_one({'date': date_receive})
   if userId in data[teamColor] :
      data[teamColor].remove(userId)
      db.dates.update_one({'date': date_receive},
                      {"$set": {teamColor: data[teamColor]}})
      
   

 
   return jsonify({'result': 'success'})

if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)

