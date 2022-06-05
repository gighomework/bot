#!/usr/bin/python
#-*-coding: utf-8 -*-
##from __future__ import absolute_import
###
from flask import Flask, jsonify, render_template, request
import json
import ezsheets
import numpy as np
import pandas as pd
import requests
import geopy.distance as ps
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,TemplateSendMessage,ImageSendMessage, StickerSendMessage, AudioSendMessage, FlexSendMessage
)
from linebot.models.template import *
from linebot import (
    LineBotApi, WebhookHandler
)

app = Flask(__name__)


lineaccesstoken = 'MMQjdcmKGYTXb21guAmbnFppUzsJbCuDloq7dsRUqOiCRccsMPUBOfuPhawY735yQ7SABUzH/J6G7ReeCFlgM0xQG388iOrY4e5WKZ6m2rPB9luNHWPPsD6+q5cd0d2NGNKdPDf+QummHK05ecXV/QdB04t89/1O/w1cDnyilFU='
line_bot_api = LineBotApi(lineaccesstoken)

casedata = pd.read_excel('casedata.xlsx')

####################### new ########################
@app.route('/')
def index():
    return "Hello World!"


@app.route('/webhook', methods=['POST'])
def callback():
    json_line = request.get_json(force=False,cache=False)
    json_line = json.dumps(json_line)
    decoded = json.loads(json_line)
    no_event = len(decoded['events'])
    for i in range(no_event):
        event = decoded['events'][i]
        event_handle(event)
    return '',200


def event_handle(event):
    print(event)
    try:
        userId = event['source']['userId']
    except:
        print('error cannot get userId')
        return ''

    try:
        rtoken = event['replyToken']
    except:
        print('error cannot get rtoken')
        return ''
    if 'message' in event.keys():
        try:
            msgType = event["message"]["type"]
            msgId = event["message"]["id"]
        except:
            print('error cannot get msgID, and msgType')
            sk_id = np.random.randint(1,17)
            replyObj = StickerSendMessage(package_id=str(1),sticker_id=str(sk_id))
            line_bot_api.reply_message(rtoken, replyObj)
            return ''
    if 'postback' in event.keys():
        msgType = 'postback'

    if msgType == "text":
        msg = str(event["message"]["text"])
        replyObj = handle_text(msg)
        line_bot_api.reply_message(rtoken, replyObj)

    if msgType == "postback":
        msg = str(event["postback"]["data"])
        replyObj = handle_postback(msg)
        line_bot_api.reply_message(rtoken, replyObj)

    if msgType == "location":
        lat = event["message"]["latitude"]
        lng = event["message"]["longitude"]
        #txtresult = handle_location(lat,lng,casedata,3)
        result = getcaseflex(lat,lng)
        replyObj = FlexSendMessage(alt_text='Flex Message alt text', contents=result)
        line_bot_api.reply_message(rtoken, replyObj)
    else:
        sk_id = np.random.randint(1,17)
        replyObj = StickerSendMessage(package_id=str(1),sticker_id=str(sk_id))
        line_bot_api.reply_message(rtoken, replyObj)
    return ''


dat = pd.read_excel('gig.xlsx')
def getdata(query):
    res = dat[dat['QueryWord']==query]
    if len(res)==0:
        return 'nodata'
    else:
        productName = res['ProductName'].values[0]
        imgUrl = res['ImgUrl'].values[0]
        desc = res['Description'].values[0]
        cont = res['Contact'].values[0]
        return productName,imgUrl,desc,cont

def flexmessage(query):
    res = getdata(query)
    if res == 'nodata':
        return ''
    else:
        productName,imgUrl,desc,cont = res
    flex = '''
   {
  "type": "carousel",
  "contents": [
    {
      "type": "bubble",
      "size": "giga",
      "hero": {
        "type": "image",
        "url": "%s",
        "size": "full",
        "aspectMode": "cover",
        "aspectRatio": "2:2.5"
      },
      "footer": {
        "type": "box",
        "layout": "horizontal",
        "contents": [
          {
            "type": "text",
            "text": "สมัครสมาชิก",
            "action": {
              "type": "uri",
              "label": "action",
              "uri": "https://bit.ly/3xbb5VC"
            },
            "weight": "bold",
            "align": "center",
            "color": "#ffffff"
          }
        ],
        "background": {
          "type": "linearGradient",
          "angle": "90deg",
          "startColor": "#e52d27",
          "endColor": "#b31217"
        }
      }
    },
    {
      "type": "bubble",
      "size": "giga",
      "hero": {
        "type": "image",
        "url": "%s",
        "size": "full",
        "aspectMode": "cover",
        "aspectRatio": "2:2.5"
      },
      "footer": {
        "type": "box",
        "layout": "horizontal",
        "contents": [
          {
            "type": "text",
            "text": "ติดต่อแอดมิน",
            "align": "center",
            "action": {
              "type": "uri",
              "label": "action",
              "uri": "https://bit.ly/38bfrT5"
            },
            "weight": "bold"
          }
        ],
        "background": {
          "type": "linearGradient",
          "angle": "90deg",
          "startColor": "#2980b9",
          "endColor": "#ffffff",
          "centerColor": "#6dd5fa"
        }
      }
    },
    {
      "type": "bubble",
      "size": "giga",
      "hero": {
        "type": "image",
        "url": "%s",
        "size": "full",
        "aspectMode": "cover",
        "aspectRatio": "2:2.5"
      },
      "footer": {
        "type": "box",
        "layout": "horizontal",
        "contents": [
          {
            "type": "text",
            "text": "ติดต่อโฆษณา",
            "action": {
              "type": "uri",
              "label": "action",
              "uri": "%s"
            },
            "align": "center",
            "weight": "bold",
            "color": "#000000"
          }
        ],
        "background": {
          "type": "linearGradient",
          "angle": "90deg",
          "startColor": "#40E0D0",
          "endColor": "#FF0080",
          "centerColor": "#FF8C00"
        }
      }
    }
  ]
}'''%(imgUrl,productName,desc,cont)
    return flex

from linebot.models import (TextSendMessage,FlexSendMessage)
import json

def handle_text(inpmessage):
    flex = flexmessage(inpmessage)
    if flex == 'nodata':
        replyObj = TextSendMessage(text=inpmessage)
    else:
        flex = json.loads(flex)
        replyObj = FlexSendMessage(alt_text='Flex Message alt text', contents=flex)
    return replyObj

def handle_postback(inpmessage):
    replyObj = TextSendMessage(text=inpmessage)
    return replyObj


def handle_location(lat,lng,cdat,topK):
    result = getdistace(lat, lng,cdat)
    result = result.sort_values(by='km')
    result = result.iloc[0:topK]
    txtResult = ''
    for i in range(len(result)):
        kmdistance = '%.1f'%(result.iloc[i]['km'])
        newssource = str(result.iloc[i]['News_Soruce'])
        txtResult = txtResult + 'ห่าง %s กิโลเมตร\n%s\n\n'%(kmdistance,newssource)
    return txtResult[0:-2]


def getcaseflex(lat,lng):
    url = 'http://botnoiflexapi.herokuapp.com/getnearcase?lat=%s&long=%s'%(lat,lng)
    res = requests.get(url).json()
    return res

def getdistace(latitude, longitude,cdat):
  coords_1 = (float(latitude), float(longitude))
  ## create list of all reference locations from a pandas DataFrame
  latlngList = cdat[['Latitude','Longitude']].values
  ## loop and calculate distance in KM using geopy.distance library and append to distance list
  kmsumList = []
  for latlng in latlngList:
    coords_2 = (float(latlng[0]),float(latlng[1]))
    kmsumList.append(ps.vincenty(coords_1, coords_2).km)
  cdat['km'] = kmsumList
  return cdat


if __name__ == '__main__':
    app.run(debug=True)
