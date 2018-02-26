

#!/usr/bin/env python

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()
from elasticsearch import Elasticsearch
from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os
import requests
from flask import Flask
from flask import request
from flask import make_response
from urllib.request import urlopen
from bs4 import BeautifulSoup
import urllib.request
import re


# Flask app should start in global layout
app = Flask(__name__)


@app.route('/chatbot', methods=['POST'])
def webhook():
	req = request.get_json(silent=True, force=True)

	print("Request:")
	res = processRequest(req)
	print(type(res))
	res = json.dumps(res, indent=4)

	r = make_response(res)
	r.headers['Content-Type'] = 'application/json'
	
	return r

@app.route('/chat', methods=['GET'])
def web():
	
	return "WELCOME :)"


def processRequest(req):
	if req.get("result").get("action") != "property":
		return {"action is empty"}
	dict={}
	result = req.get("result").get("parameters")
	print(result)
	resolvedQuery=req.get("result").get("resolvedQuery")
	print("Resolved Query",resolvedQuery)

	
	try:
		num_rooms = result.get("Rooms")
	except:
		num_rooms = 1
	try:
		location = result.get("Location")
	except:
		location = "Al Raheen"

	sQuery=str(num_rooms)+"in"+str(location)+" "
	result=elas_search(num_rooms,location)
	if result=="No Results":
		return {
		"speech":"webhook works",
		"display text":"webhook works",
		"messages":[
		{
		"type":1,
		"platform":"skype",
		"title":"Sorry!",
		"buttons":[
		 {
		 "text":"We currently don’t"+"\n"+" have any properties "+"\n"+"in this location"
		 }


		]
	}
	]
	}
	else:
		res = makeWebhookResult(result)
		return res





def makeWebhookResult(data):
	price_type=[]
	price=[]

	for item in data:
		if item.get('_source'):
			if str(item['_source']["sale_price"]) == "0":
				price_type.append("lease_price")
				price.append(item['_source']["lease_price"])
			else:
				price_type.append("sale_price")
				price.append(item['_source']["sale_price"])
		
	
	try:
		sample_json={
		"speech":"webhook works",
		"display text":"webhook works",
		"messages":[
		{
		"type":1,
		"platform":"skype",
		"title":data[0]["_source"]["Property Name"],
		"subtitle": data[0]["_source"]["Destination"]+","+"\n"+data[0]["_source"]["UnitType"]+","+"\n"+price_type[0]+":"+price[0]+","+"\n"+"Code:"+data[0]["_source"]["LocationCode"],
		"buttons":[
		 {
		 "text":data[0]["_source"]["Unit_plan"]
		 }


		]
	},
	{
		"type":1,
		"platform":"skype",
		"title":data[1]["_source"]["Property Name"],
		"subtitle": data[1]["_source"]["Destination"]+","+"\n"+data[1]["_source"]["UnitType"]+","+"\n"+price_type[1]+":"+price[1]+","+"\n"+"Code:"+data[1]["_source"]["LocationCode"],
		"buttons":[
		 {
		 "text":data[1]["_source"]["Unit_plan"]
		 }
		]
	},
	{
		"type":1,
		"platform":"skype",
		"title":data[2]["_source"]["Property Name"],
		"subtitle": data[2]["_source"]["Destination"]+","+"\n"+data[2]["_source"]["UnitType"]+","+"\n"+price_type[2]+":"+price[2]+","+"\n"+"Code:"+data[2]["_source"]["LocationCode"],
		"buttons":[
		 {
		 "text":data[2]["_source"]["Unit_plan"]
		 }

		]
	}
		]
	}

		return sample_json
	except Exception as error:
		print(error)	
	
	return {
		"speech":"webhook works",
		"display text":"webhook works",
		"messages":[
		{
		"type":1,
		"platform":"skype",
		"title":data[0]["_source"]["Property Name"],
		"subtitle": data[0]["_source"]["Destination"]+","+"\n"+data[0]["_source"]["UnitType"]+","+"\n"+price_type[0]+":"+price[0]+","+"\n"+"Code:"+data[0]["_source"]["LocationCode"],
		"buttons":[
		 {
		 "text":data[0]["_source"]["Unit_plan"]
		 }
		]
	}
	]
	}
	

	  

			
def elas_search(num_rooms,location):
	es = Elasticsearch('http://10.16.92.63:9200/')
	print("inside elasticsearch")
	print(num_rooms)
	print(location)
	res = es.search(index="aldar", doc_type="prop",
	body={"query":
	 {"bool": 
	 {"must": 
	 [
	 { "match": { "Destination": location}
	 },
	 { "match": { "Bedrooms": num_rooms }
	 }
	 ]
	}
	}})

	print("%d documents found" % res['hits']['total'])

	if str(res['hits']['total'])=="0":
		return "No Results"
	else:
	
		return res['hits']['hits']


#google scraping		

# def search(query):
	
# 	query=query.strip().split()
# 	query="+".join(query)
# 	html="https://www.google.co.in/search?q="+query
# 	req = urllib.request.Request(html, headers={'User-Agent': 'Mozilla/5.0 '})
# 	soup = BeautifulSoup(urlopen(req).read(),"html.parser")
# 	projLink=[]
# 	projDetail=[]
# 	projImage=[]
# 	projDesc=[]
# 	projDescList=[]
# 	project=[]
# 	h3tags = soup.find_all( 'h3', class_='r' )
# 	for h3 in h3tags:
# 		  try:
# 			  projDetail.append(h3.a.text)
# 			  projLink.append( re.search('url\?q=(.+?)\&sa', h3.a['href']).group(1) )
# 		  except:
# 			  continue

# 	project.append(projLink)
# 	project.append(projDetail)
# 	project.append(projImage)
# 	project.append(projDesc)	
# 	project.append(projDescList)
		

# 	return project
   
	   


if __name__ == '__main__':
	port = int(os.getenv('PORT', 8000))

	print("Starting app on port %d" % port)

	app.run(debug=False, port=port, host='0.0.0.0')

