from pymongo import MongoClient

import requests
from bs4 import BeautifulSoup

from flask import Flask, render_template, jsonify, request
app = Flask(__name__)

client = MongoClient('localhost', 27017)
#db변경해줄것!
db = client.dbsparta

# HTML을 주는 부분
@app.route('/')
def home():
    return render_template('mypage.html')

@app.route('/mypage')
def mypage():
    return render_template('mypage.html')

@app.route('/write')
def write():
    return render_template('write.html')

@app.route('/write_ing')
def write_ing():
    return render_template('write_ing.html')

@app.route('/write_read')
def write_read():
    return render_template('write_read.html')

@app.route('/transcribe')
def transcribe():
    return render_template('transcribe.html')

@app.route('/transcribe2')
def transcribe2():
    return render_template('transcribe2.html')

@app.route('/scrap')
def scrap():
    return render_template('scrap.html')

#####################################################################################
###########scrap.html에서 list & save
@app.route('/list/article', methods=['GET'])
def list_article():
    # 1. 모든 document 찾기 & _id 값은 출력에서 제외하기
    result = list(db.articles.find({}, {'_id': 0}) )
    # 2. articles라는 키 값으로 영화정보 내려주기
    return jsonify({'result':'success', 'msg':'GET 연결되었습니다!','articles':result})

## API 역할을 하는 부분
@app.route('/save/article', methods=['POST'])
def saving_article():
    # 1. 클라이언트로부터 데이터를 받기
    url_receive = request.form['url_give']  # 클라이언트로부터 url을 받는 부분
    comment_receive = request.form['comment_give']  # 클라이언트로부터 comment를 받는 부분

    # 2. meta tag를 스크래핑하기
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url_receive, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')

    og_image = soup.select_one('meta[property="og:image"]')
    og_title = soup.select_one('meta[property="og:title"]')
    og_description = soup.select_one('meta[property="og:description"]')

    url_image = og_image['content']
    url_title = og_title['content']
    url_description = og_description['content']

    article = {'url': url_receive, 'comment': comment_receive, 'image': url_image,
               'title': url_title, 'desc': url_description}

    # 3. mongoDB에 데이터를 넣기
    db.articles.insert_one(article)

    return jsonify({'result': 'success', 'msg':'POST 연결되었습니다!'})
############################################################################################
#write()

import time

@app.route('/save/mine', methods=['POST'])
def save_mine():
    # 1. 클라이언트로부터 데이터를 받기
    title_receive = request.form['title_give']  # 클라이언트로부터 url을 받는 부분
    topic_receive = request.form['topic_give']
    content_receive = request.form['content_give']

    times = time.strftime('%Y-%m-%d (%H:%M)', time.localtime(time.time()))

    # 3. mongoDB에 데이터를 넣기
    myarticle = {'title' : title_receive , 'topic':topic_receive , 'content':content_receive , 'time':times}
    db.myarticle.insert_one(myarticle)

    return jsonify({'result': 'success', 'msg':'작성한 기사가 저장되었습니다!'})

@app.route('/list/mine', methods=['GET'])
def list_mine():
    # 1. 모든 document 찾기 & _id 값은 출력에서 제외하기
    result = list(db.myarticle.find({}, {'_id': 0}))
    # 2. articles라는 키 값으로 영화정보 내려주기
    return jsonify({'result':'success', 'msg':'GET 연결되었습니다!', 'mine':result})

############################################################################################
# transcribe()
import re

@app.route('/check_article', methods=['GET'])
def check_article():
    # 1. 클라이언트로부터 데이터를 받기
    url_receive = request.args.get('url_give')  # 클라이언트로부터 url을 받는 부분

    # 2. meta tag를 스크래핑하기
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url_receive, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')

    og_image = soup.select_one('meta[property="og:image"]')
    og_title = soup.select_one('meta[property="og:title"]')
    og_description = soup.select_one('meta[property="og:description"]')
    og_body = soup.select('#articleBodyContents')
    og_ogurl = soup.select('#main_content > div > div >div > a ')

    text_temp = ""
    for body in og_body :
        a_tag = body.text
        if a_tag is not None:
            text_temp += a_tag

    url_body = text_temp
    url_image = og_image['content']
    url_title = og_title['content']
    url_description = og_description['content']
    print(url_title)

    num=0
    temp_url={}
    for body in og_ogurl :
        a_tag = body['href']
        temp_url[num] = a_tag
        print(num , a_tag)
        num+=1

    ogurl = temp_url[0]

    article = {'url' : url_receive,'image': url_image, 'title': url_title, 'desc': url_description , 'body' : url_body , 'ogurl' : ogurl}
    return jsonify({'result': 'success', 'msg':'연결되었습니다!', 'articles' : article})


if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)

