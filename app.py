# program 종료하려면 Ctrl+C
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from pymongo import MongoClient
client  = MongoClient('localhost', 27017)
db = client.rgbuddy

app = Flask(__name__)



@app.route('/')
def home():
   return render_template('index.html')


@app.route('/signup', methods= ['POST'])
def signup():
    id_receive = request.form['id_give']  
    pw_receive = request.form['pw_give']
    name_receive = request.form['name_give']
    team_receive = request.form['team_give']
    phone_receive = request.form['phone_give']


    user = {'id': id_receive, 'password': pw_receive, 'name' : name_receive, 
            'phone': phone_receive, 'team': team_receive}
    db.users.insert_one(user)

    return jsonify({'result': 'success'})
    


@app.route('/login', methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['id_give']
        password = request.form['pw_give']
        # 로그인 정보 검증 로직 작성

        # 로그인 정보가 올바르면 세션에 사용자 정보 저장
        session['username'] = username
        return redirect(url_for('index'))

    return render_template('login.html')





    
#GET으로 날짜값을 넘겨준다음, 그 날짜에 해당하는 


@app.route('/matching', methods = ['GET'])
def matching():

    #(추가필요) 로그인이 되어있는지 확인해야 함.
    
    
    date = request.args.get('date')
    
    #받아온 date로 db에서 각 팀에 저장된 사람의 수를 불러옴
    query = {'date': date}
    
    data = list(db.dates.find(query))
 
    redCount = len(data[0]['red'])
    blueCount = len(data[0]['blue'])
    greenCount = len(data[0]['green'])

    return render_template('matching.html', redCount=redCount, blueCount=blueCount, greenCount=greenCount)



  
    
    
    

    
    
        

if __name__ == '__main__':  
   app.run('0.0.0.0',port=5000,debug=True)




