#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#author z3jjlzt
# -u 用户歌单　-s 歌手专辑 -t 单曲 默认华语歌单

import requests
import base64
import hashlib
import json
import os
import sys

class wyyyy(object):
	headers = {
		'Host': 'music.163.com',
		'Proxy-Connection': 'keep-alive',
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.76 Safari/537.36',
		'Content-Type': 'application/x-www-form-urlencoded',
		'Accept': '*/*',
		'Referer': 'http://music.163.com/',
		'Accept-Encoding': 'gzip, deflate, sdch',
		'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
		'Cookie': 'appver=1.5.0.75771',
		}
	param = {"type":"1002","s":"z3jjlzt","offset":"0"}
	search = "http://music.163.com/api/search/get/"

	# 搜索模式
	def selectType(self):
		if(len(sys.argv) < 2):
			return
		if(sys.argv[1] == "-u"):
			self.param["type"] = "1002"
		elif(sys.argv[1] == "-s"):
			self.param["type"] = "100"
		elif(sys.argv[1] == "-t"):
			self.param["type"] = "1"
		self.param["s"] = sys.argv[2]
		self.param["offset"] = 0
		return self.param

	#default
	def getDefault(self,param, category='华语', order='hot', limit=20):
		r = requests.post("http://music.163.com/api/playlist/list?cat="+category+"&limit="+str(limit)+"&order="+order,data=self.param,headers=self.headers)
		dict = {}
		tmpName = {}
		txt = json.loads(r.text)
		size = 0
		for i,x in enumerate(txt['playlists']):
			print(i,x['name'])
			dict[i] = x['id']
			tmpName[i] = x['name']
			size = i
		select=input("input your select item -> ")
		while(not select.isdigit() or int(select) > size or int(select) < 0):
			select=input("input number only -> ")
		r = requests.get("http://music.163.com/api/playlist/detail?id="+str(dict[int(select)]))

		#具体歌单信息
		src = json.loads(r.text)

		songdict = {}
		for i,x in enumerate(src['result']['tracks']):
			songdict[x['name']]=x['mp3Url']
			
		return tmpName[int(select)],songdict
		
	# 按用户名搜索
	def getUserList(self,param):
		while True:
			r = requests.post(self.search,data=self.param,headers=self.headers)
			txt = json.loads(r.text)
			if(txt['result']['userprofileCount'] > 0):
				id=str(txt['result']['userprofiles'][0]['userId'])
				break
			if(txt['result']['userprofileCount'] == 0):
				self.param['s']=input("未找到此用户，请重新输入 -> ")
		lst = requests.get("http://music.163.com/api/user/playlist/?offset=0&limit=1001&uid="+id)

		#歌单列表
		l = json.loads(lst.text)

		size = 0
		for i,x in enumerate(l['playlist']):
			print(i,x['name'])
			size = i
		select=input("input your select item -> ")
		while(not select.isdigit() or int(select) > size or int(select) < 0):
			select=input("input number only -> ")

		lstid = ""
		lstName = ""
		for i,x in enumerate(l['playlist']):
			if(int(i)==int(select)):
				lstid=x['id']
				lstName = x['name']
		r = requests.get("http://music.163.com/api/playlist/detail?id="+str(lstid))

		#具体歌单信息
		src = json.loads(r.text)

		songdict = {}
		for i,x in enumerate(src['result']['tracks']):
			songdict[x['name']]=x['mp3Url']
			
		return lstName,songdict
	# 按歌手搜索	
	def getAlbumList(self,param):

		#得到歌手id
		while True:
			r = requests.post(self.search,data=self.param,headers=self.headers)
			txt = json.loads(r.text)
			if(txt['result']['artistCount'] > 0):
				break
			if(txt['result']['artistCount'] == 0):
				self.param['s'] = input("未找到该歌手，请重新输入 -> ")

		singerId = str(txt['result']['artists'][0]['id'])

		#得到所有专辑列表 limit 返回专辑数量
		txt = json.loads(requests.get("http://music.163.com/api/artist/albums/"+singerId+"/?limit=1001",headers=self.headers).text)
		size = 0
		for i,x in enumerate(txt['hotAlbums']):
			print(i,x['name'],)
			size = i
		select=input("input your select album -> ")
		while(not select.isdigit() or int(select) > size or int(select) < 0):
			select=input("input number only -> ")
		lstid = ""
		albumName = ""
		for i,x in enumerate(txt['hotAlbums']):
			if(int(i) == int(select)):
				lstid = str(x['id'])
				albumName = x['name']
		
		#得到专辑歌曲列表
		songdict = {}
		txt = json.loads(requests.get("http://music.163.com/api/album/"+lstid+"/?limit=1001",headers=self.headers).text)
		for i,x in enumerate(txt['album']['songs']):
			songdict[x['name']]=x['mp3Url']
		return albumName,songdict

	#按单曲搜索
	def getBySingle(self,param):
		while True:
			r = requests.post(self.search,data=param,headers=self.headers)
			txt = json.loads(r.text)
			if(txt['code'] == 200):
				break
			elif(txt['code'] != 200):
				param['s'] = input("未找到该歌曲，请重新输入 -> ")
		
		print(txt['result']['songCount'])
		lst = txt['result']['songs']
		songdict = {}
		tmplst = {}
		size = 0
		for i,x in enumerate(lst):
			tid = str(lst[i]['id'])
			print(i,lst[i]['artists'][0]['name'],lst[i]['album']['name'])
			r = requests.post("http://music.163.com/api/song/detail/?id="+tid+"&ids=%5B"+tid+"%5D",data=param,headers=self.headers)
			txt = json.loads(r.text)
			songdict[lst[i]['artists'][0]['name']+"   "+lst[i]['album']['name']] = txt['songs'][0]['mp3Url']
			tmplst[i] = {lst[i]['artists'][0]['name']+"   "+lst[i]['album']['name']:txt['songs'][0]['mp3Url']}
			size = i
		select = input("input your select song -> ")
		while(not select.isdigit() or int(select) > size or int(select) < 0):
			select = input("input number only -> ")
		return param['s'],tmplst[int(select)]
	
	def play(self,albunName,songdict):
		os.system("mocp -S ")
		os.system("mocp -c")
		player="mocp ^u "
		print("########################")
		print("      " + albumName)
		for k,v in songdict.items():
			player += "\'" + v + "                                                          " + k + "\' "
			print(k)
		print("########################")
		os.system(player)

	def writeToFile(self,albunName,songdict):
		with open(os.path.dirname(os.path.realpath(__file__))+'/songLst.txt','a') as f:
			f.write("songLst " + albunName+ "\n")
			for k,v in songdict.items():
				f.write(v + " " + k + "\n")
			f.write("\n")


	def playBympg(self,albunName,songdict):
		player="mpg123 -C --title -v -u a "
		print("########################")
		print("      " + albumName)
		for k,v in songdict.items():
			player += v + " "
			print(k)
		print("########################")
		os.system(player)

# md5加密
def encrypted_id(id):
	magic = bytearray('3go8&$8*3*3h0k(2)2', 'u8')
	song_id = bytearray(str(id), 'u8')
	magic_len = len(magic)
	for i, sid in enumerate(song_id):
		song_id[i] = sid ^ magic[i % magic_len]
	m = hashlib.md5(song_id)
	result = m.digest()
	result = base64.b64encode(result)
	result = result.replace(b'/', b'_')
	result = result.replace(b'+', b'-')
	return result.decode('u8')

client = wyyyy()
param = client.selectType()
if(len(sys.argv) > 2):
	if(sys.argv[1] == "-s"):
		albumName,songdict = client.getAlbumList(param)
	elif(sys.argv[1] == "-u"):
		albumName,songdict = client.getUserList(param)
	elif(sys.argv[1] == "-t"):
		albumName,songdict = client.getBySingle(param)
else:
	albumName,songdict = client.getDefault(param)
client.writeToFile(albumName,songdict)
client.playBympg(albumName,songdict)
