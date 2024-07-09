import math

from flask import Flask, render_template, request, flash, session, redirect
from random import shuffle
import pandas as pd
import numpy as np
from collections import Counter

# perhitungan
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn import metrics

app = Flask(__name__)
app.secret_key = 'super secret'

@app.route('/hasil', methods=['GET'])
def hasil():
	if ('jawaban' not in session) or (len(session['jawaban']) < 17):
		flash('Anda belum menjawab pertanyaan!!!')
		return redirect('/')
	
	inputan = {
		'Waktu di atas kasur (rebahan sampai bangun pagi) (Jam)': [session['jawaban']['1']],
		'Waktu rebahan sebelum tertidur (Menit)': [session['jawaban']['2']],
		'Waktu tertidur (Jam)': [session['jawaban']['3']],
		'Tidak dapat tertidur dalam 30 menit': [session['jawaban']['4']],
		'bangun tengah malam atau dini hari': [session['jawaban']['5']],
		'bangun ke kamar mandi': [session['jawaban']['6']],
		'tidak dapat bernafas dengan baik saat tertidur': [session['jawaban']['7']],
		'batuk atau mendengkur': [session['jawaban']['8']],
		'kedinginan saat tertidur': [session['jawaban']['9']],
		'kepanasan saat tertidur': [session['jawaban']['10']],
		'terbangun karena mimpi buruk': [session['jawaban']['11']],
		'merasakan nyeri saat tertidur': [session['jawaban']['12']],
		'gangguan lain saat tertidur': [session['jawaban']['13']],
		'konsumsi obat tidur': [session['jawaban']['14']],
		'mengantuk pada saat beraktifitas': [session['jawaban']['15']],
		'memikirkan masalah saat beraktifitas': [session['jawaban']['16']],
		'kualitas tidur secara objektif': [session['jawaban']['17']],
	}

	inputan = pd.DataFrame(inputan)

	# tampilkan
	items = pd.read_csv('dataset.txt', sep=';')
	items.columns = range(items.shape[1])

	# mendapatkan nilai x dan y
	df_raw = pd.read_csv('dataset-raw.txt', sep=';')
	df_raw['Kualitas tidur']=df_raw['Kualitas tidur'].map({'Baik':0,'Buruk':1})
	x = df_raw.drop(['Kualitas tidur'], axis=1)
	y = df_raw['Kualitas tidur']

	# Modelling
	x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.35, random_state = 0)

	knn = KNeighborsClassifier(n_neighbors=4)
	knn.fit(x_train, y_train)

	pred = knn.predict(inputan)

	df = df_raw.to_html(classes='table table-striped table-hover table-bordered table-sm table-responsive-sm'), 

	label = {0: 'Baik', 1: 'Buruk'}

	inputan = pd.DataFrame(inputan)
	inputan = inputan.rename(index={0: 'Inputan'})
	inputan = inputan.transpose()

	return render_template(
		'hasil.html', 
		jawaban=session['jawaban'], 
		pred=label[pred[0]],
		inputan = inputan.to_html(classes='table table-striped table-hover table-bordered table-sm table-responsive-sm'),
	)

@app.route('/pertanyaan/<id>', methods=['GET','POST'])
def tanya(id):
	pertanyaan = {
		"1" : 'Selama sebulan terakhir, berapa jam tiap malam yang anda habiskan di atas Kasur? (dari mulai rebahan di atas Kasur sampai bangun pagi)',
		"2" : 'Selama sebulan terakhir, Berapa lama (dalam menit) yang anda perlukan untuk dapat mulai tertidur setiap malam? (Waktu Yang Dibutuhkan Saat Mulai Berbaring Hingga Tertidur)',
		"3" : 'Selama sebulan terakhir, berapa jam tiap malam yang anda habiskan saat tidur? (dari mulai tertidur hingga terbangun pada pagi hari)',
		"4" : 'Selama sebulan terakhir, seberapa sering anda Tidak dapat tidur di malam hari dalam waktu 30 menit',
		"5" : 'Selama sebulan terakhir, seberapa sering anda Bangun tengah malam atau dini hari',
		"6" : 'Selama sebulan terakhir, seberapa sering anda Harus bangun untuk ke kamar mandi',
		"7" : 'Selama sebulan terakhir, seberapa sering anda Tidak dapat bernafas dengan nyaman saat berbaring',
		"8" : 'Selama sebulan terakhir, seberapa sering anda Batuk atau mendengkur keras',
		"9" : 'Selama sebulan terakhir, seberapa sering anda terbangun karena merasa kedinginan saat sedang tidur',
		"10" : 'Selama sebulan terakhir, seberapa sering anda terbangun karena merasa kepanasan saat sedang tidur',
		"11" : 'Selama sebulan terakhir, seberapa sering anda anda terbangun karena mimpi buruk saat sedang tidur',
		"12" : 'Selama sebulan terakhir, seberapa sering anda anda terbangun karena merasakan nyeri saat sedang tidur',
		"13" : 'Selama sebulan terakhir, seberapa sering anda penyebab lain yang belum disebutkan di atas yang menyebabkan anda terganggu di malam hari dan seberapa sering anda mengalaminya? (Contoh: Mengigau)',
		"14" : 'Selama sebulan terakhir, seberapa sering anda mengkonsumsi obat tidur(diresepkan oleh dokter ataupun obat bebas) untuk membantu anda tidur?',
		"15" : 'Selama sebulan terakhir, seberapa sering anda merasa mengantuk ketika melakukan aktifitas mengemudi, makan atau aktifitas sosial lainnya?',
		"16" : 'Selama sebulan terakhir, seberapa sering anda adakah masalah yang anda hadapi untuk bisa berkonsentrasi atau menjaga rasa antusias untuk menyelesaikan suatu pekerjaan/tugas?',
		"17" : 'Selama sebulan terakhir, bagaimana menurut anda kualitas tidur anda?',
	}

	if int(id) == 1:
		session.pop('jawaban', None)

	if 'jawaban' not in session:
		session['jawaban'] = {}

	if request.method == 'POST':
		session['jawaban'][str(int(id)-1)] = request.form['jawaban']
		session.modified = True
		
		return redirect('/pertanyaan/' + str(id))
	
	elif request.method == 'GET':
		if(int(id) > 17):
			return redirect('/hasil')
		
		pertanyaan = pertanyaan[id]
		id = int(id) + 1;
		return render_template('base.html', pertanyaan=pertanyaan, id=id, jawaban=session['jawaban'], jumlah=len(session['jawaban']))

@app.route('/pertanyaan', methods=['GET','POST'])
def pertanyaan():

	if request.method == 'POST':
		data_1		= int(request.form['1'])
		data_2		= int(request.form['2'])
		data_3 		= int(request.form['3'])
		data_4		= int(request.form['4'])
		data_5		= int(request.form['5'])
		data_6		= int(request.form['6'])
		data_7		= int(request.form['7'])
		data_8		= int(request.form['8'])
		data_9		= int(request.form['9'])
		data_10		= int(request.form['10'])
		data_11		= int(request.form['11'])
		data_12		= int(request.form['12'])
		data_13		= int(request.form['13'])
		data_14		= int(request.form['14'])
		data_15		= int(request.form['15'])
		data_16		= int(request.form['16'])
		data_17		= int(request.form['17'])
		k 			= int(request.form['k'])
		

		inputan = {
			'Waktu di atas kasur (rebahan sampai bangun pagi) (Jam)': [data_1],
			'Waktu rebahan sebelum tertidur (Menit)': [data_2],
			'Waktu tertidur (Jam)': [data_3],
			'Tidak dapat tertidur dalam 30 menit': [data_4],
			'bangun tengah malam atau dini hari': [data_5],
			'bangun ke kamar mandi': [data_6],
			'tidak dapat bernafas dengan baik saat tertidur': [data_7],
			'batuk atau mendengkur': [data_8],
			'kedinginan saat tertidur': [data_9],
			'kepanasan saat tertidur': [data_10],
			'terbangun karena mimpi buruk': [data_11],
			'merasakan nyeri saat tertidur': [data_12],
			'gangguan lain saat tertidur': [data_13],
			'konsumsi obat tidur': [data_14],
			'mengantuk pada saat beraktifitas': [data_15],
			'memikirkan masalah saat beraktifitas': [data_16],
			'kualitas tidur secara objektif': [data_17],
		}

		inputan = pd.DataFrame(inputan)

		# tampilkan
		items = pd.read_csv('dataset.txt', sep=';')
		items.columns = range(items.shape[1])

		# mendapatkan nilai x dan y
		df_raw = pd.read_csv('dataset-raw.txt', sep=';')
		df_raw['Kualitas tidur']=df_raw['Kualitas tidur'].map({'Baik':0,'Buruk':1})
		x = df_raw.drop(['Kualitas tidur'], axis=1)
		y = df_raw['Kualitas tidur']

		# Modelling
		x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.35, random_state = 0)

		knn = KNeighborsClassifier(n_neighbors=4)
		knn.fit(x_train, y_train)

		pred = knn.predict(inputan)

		df = df_raw.to_html(classes='table table-striped table-hover table-bordered table-sm table-responsive-sm'), 

		label = {0: 'Baik', 1: 'Buruk'}

		inputan = pd.DataFrame(inputan)
		inputan = inputan.rename(index={0: 'Inputan'})
		inputan = inputan.transpose()


    # status = label[pred]

		# print("Hasil Prediksi: " + str(pred))

		return render_template(
			'base.html',
			inputan = inputan.to_html(classes='table table-striped table-hover table-bordered table-sm table-responsive-sm'), 
			pred=label[pred[0]], 
			k=k)
	
	return render_template('base.html')

@app.route('/')
def index():
	session.pop('jawaban', None)
	return render_template('landing.html')

@app.route('/dataset')
def dataset():
	# Ambil data dari dataset
	items = pd.read_csv('dataset-raw.txt', sep=';')
	items['Kualitas tidur']=items['Kualitas tidur'].map({'Baik':0,'Buruk':1})

	# data
	items = items.to_html(classes='table table-striped table-hover table-bordered table-sm table-responsive text-xs')

	# tampilkan
	return render_template('dataset.html', items=items)

if __name__ == '__main__':
	app.run(debug=True, port=5000)