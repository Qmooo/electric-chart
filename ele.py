import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from flask_cors import CORS
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
mongo_host = os.environ.get('MONGO_HOST', 'mongodb')
mongo_port = os.environ.get('MONGO_PORT', '27017')
mongo_username = os.environ.get('MONGO_USERNAME', 'admin')
mongo_password = os.environ.get('MONGO_PASSWORD', 'password')

app = Flask(__name__)
url = "http://59.127.49.50/"

def get_electric_balance(Room, Phone):
    body = {
        '__EVENTTARGET': '',
        '__EVENTARGUMENT':'', 
        'ctl00$Content$BootstrapFormLayout1$edRoomNo': Room,
        'ctl00$Content$BootstrapFormLayout1$edPhone': Phone,
        'ctl00$Content$BootstrapFormLayout1$btnQuery': '查詢',
    }
    response = requests.post(url, data=body)
    bs4 = BeautifulSoup(response.content, 'html.parser')
    edBalance = bs4.find('input', attrs={'id': 'Content_BootstrapFormLayout1_edBalance_I'})['value']
    time = bs4.find('input', attrs={'id': 'Content_BootstrapFormLayout1_edQueryTime_I'})['value']
    return edBalance, time

def connect_mongo():
    client = MongoClient(
        host = mongo_host, 
        port = int(mongo_port),
        username = mongo_username,
        password = mongo_password,)

    db = client['ele']
    collection = db['ele']
    return collection

def insert_mongo():
    collection = connect_mongo()
    Room = os.environ.get('ROOM')
    Phone = os.environ.get('PHONE')
    edBalance, time = get_electric_balance(Room, Phone)
    collection.insert_one({'Room': Room, 'Time': time, 'edBalance': edBalance})
    print(f"New data inserted. Time: {time}, Balance: {edBalance}")

apscheduler = BackgroundScheduler()
apscheduler.add_job(insert_mongo, 'interval', hours=1)
apscheduler.start()


@app.route('/')
def index():
    collection = connect_mongo()
    appointments = list(collection.find())
    for appointment in appointments:
        appointment.pop('_id')
    data = jsonify(appointments)
    return render_template('index.html', data=data.json)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=30800, debug=True)

