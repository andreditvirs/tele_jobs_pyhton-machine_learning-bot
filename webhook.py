# -*- coding: utf-8 -*-
from flask import Flask,render_template,url_for,request
import pickle
import json
import pandas as pd
import requests

app = Flask(__name__)

@app.route('/predict',methods=['POST'])
def predict():
	results = requests.get("https://api.telegram.org/bot6004748378:AAGjqym8DMEj60N3-f59NXIuQewty8rDbCs/getUpdates")
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

		for result in results['result']:
			chat_id_from = result['message']['chat']['id']
			message = result['message']['text']
			data = [message]
			vect = loaded_vectorizer.transform(data)
			output = loaded_model.predict(vect)
			prediction.status = "ok"
			prediction.message = "Data is retrieved successfuly"

			if(int(output)):
				# text_prediction = "Halo kak, untuk kenyamanan bersama mohon untuk tidak mengirimkan pesan yang menyimpang dari topik obrolan grup yaa. Yuk kirim lagi pesan yang berkaitan dengan lowongan pekerjaan! —JoobseekBot"
				text_prediction = "hi"
			requests.get("https://api.telegram.org/bot6004748378:AAGjqym8DMEj60N3-f59NXIuQewty8rDbCs/sendMessage?parse_mode=HTML&chat_id="+str(chat_id_from)+"&text="+text_prediction)
	except BaseException as e:
		prediction.message = str(e)
		return prediction.to_json()
if __name__ == '__main__':
	app.run(debug=True)
	
