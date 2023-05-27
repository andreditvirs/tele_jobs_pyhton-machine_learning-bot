#!/usr/bin/env python
# -*- coding: utf-8 -*- 

# from flask import Flask,render_template,url_for,request
import sys

if (sys.version_info.major >= 3):
    from urllib.parse import urlparse
else:
    from urlparse import urlparse
    
import urllib.parse
import pickle
import json
import pandas as pd
import requests
import time

# app = Flask(__name__)

# @app.route('/predict',methods=['POST'])
def predict():
	token = "6117835761:AAEGYEDHUjqfHj3tTPcq3VqdfS-2PTjmHbs"
	file_offset = open('offset_update_id.txt', 'r+')
	last_update_id = file_offset.read()
	file_offset.close()
	results = requests.get("https://api.telegram.org/bot"+token+"/getUpdates")
	if last_update_id:
		results = requests.get("https://api.telegram.org/bot"+token+"/getUpdates?offset="+last_update_id)
	results = results.json()

	prediction = pd.Series({'status': "fail", 'message': "Internal Server Erorr", 'data': {'output': []}})
	
	try:
		# load the vectorizer
		f1 = open('./assets/model/job_spam_vect.pickle', 'rb')
		loaded_vectorizer = pickle.load(f1)
		f1.close()

		# load the model
		f2 = open('./assets/model/job_spam_model.model', 'rb')
		loaded_model = pickle.load(f2)
		f2.close()

		for result in reversed(results['result']):
			if str(result["update_id"]) != str(last_update_id):
				file_offset = open('offset_update_id.txt', 'w')
				file_offset.write(str(result["update_id"]))
				file_offset.close()

				chat_id_from = result['message']['chat']['id']
				message = result['message']['text']
				data = [message]
				vect = loaded_vectorizer.transform(data)
				output = loaded_model.predict(vect)
				prediction.status = "ok"
				prediction.message = "Data is retrieved successfuly"

				if(int(output)):
					requests.get("https://api.telegram.org/bot"+token+"/deleteMessage?chat_id="+str(chat_id_from)+"&message_id="+str(result["message"]["message_id"]))
					text_prediction = "Halo kak <b>"+result["message"]["from"]["first_name"]+"</b>, untuk kenyamanan bersama mohon untuk tidak mengirimkan pesan yang menyimpang dari topik obrolan grup yaa. Yuk kirim lagi pesan yang berkaitan dengan lowongan pekerjaan! 🙌\n—<i>JoobseekBot</i> ☺️"
					response = requests.get("https://api.telegram.org/bot"+token+"/sendMessage?parse_mode=HTML&chat_id="+str(chat_id_from)+"&text="+urllib.parse.quote(text_prediction, safe=''))
					response = response.json()
					time.sleep(8)
					requests.get("https://api.telegram.org/bot"+token+"/deleteMessage?chat_id="+str(response["result"]["chat"]["id"])+"&message_id="+str(response["result"]["message_id"]))
			else:
				exit()
	except BaseException as e:
		prediction.message = str(e)
		return prediction.to_json()
if __name__ == '__main__':
	for i in range(3500):
		predict()
		time.sleep(1)
	exit()
	# app.run(debug=True)
	
