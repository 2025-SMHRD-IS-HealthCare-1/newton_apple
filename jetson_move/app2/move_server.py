# jetson_move/app2/move_server.py

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pymysql

from fastapi import FastAPI, Request, UploadFile, File, HTTPException 
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from jetbot import Robot
import time
from RGB_Lib import Programing_RGB
from jetbot import Camera
from jetbot import bgr8_to_jpeg
import cv2
import requests
import os
import threading
import json
import re
# import streamlit as st

# 카메라 초기화
camera = Camera.instance(width=224, height=224)

# 저장 폴더 생성
save_dir = '/home/jetbot/jetbot/pictures'
os.makedirs(save_dir, exist_ok=True)

# print("✅ 0.1초 간격으로 자동 촬영 시작 (Ctrl + C 로 중단)")
FILE_PATH = "/home/jetbot/jetbot/pictures/apple.jpg"
SERVER_URL = "http://localhost:8000/predict"  # 서버 주소로 변경하세요

# files = {"file": (uploaded.name, io.BytesIO(file_bytes), uploaded.type or "image/jpeg")}

def go_stop(str):
    print('go_stop : ',str)

def worker(name):
    try:
        while True:
            # stilcut create
            frame = camera.value  # 현재 프레임 (numpy array, BGR 형식)
            timestamp = time.strftime("%Y%m%d-%H%M%S")
#             ms = int((time.time() * 1000) % 10)  # 밀리초 추가
    #         filename = os.path.join(save_dir, f"apple_{timestamp}-{ms:03d}.jpg")
            filename = os.path.join(save_dir, f"apple.jpg")

            cv2.imwrite(filename, frame)
#             print(f"📸 저장됨: {filename}")

            # image send
            with open(FILE_PATH, 'rb') as f:
#                 files = {'file': f}
                # filename, file object, Content-Type 순서로 지정
                files = {'file': ('apple.jpg', f, 'image/jpeg')}
                response = requests.post(SERVER_URL, files=files)
#                 print(f"전송 완료 ({response.status_code}): {response.text}")
#                 data_jaeho= json.loads(response.text)
#                 print(f" if : {data_jaeho["detections"][0]["cls"]}")
#                 match = re.search(r'"score"\s*:\s*"([^"]+)"', response.text)
                match = re.search(r'"score"\s*:\s*([0-9.]+)', response.text)
                if match:
                    score_value = round(float(match.group(1)),2)
                    print(score_value)  # 0.42699679732322693
                    
                    if score_value>=0.3:
                        robot.forward(1) 
                    elif score_value is None : 
                        robot.stop() 
                    else :
                        robot.stop() 
                else :
                    robot.stop() 
                        
                
            time.sleep(0.3)  # 0.1초 간격 (100ms)
#             return {response.text}
            

    except KeyboardInterrupt:
        print("🛑 촬영 중단됨.")

    finally:
        camera.stop()
        print("📷 카메라 종료 완료.")

        
        
        
app = FastAPI(title="Jetson FastAPI (move)", version="1.0.0")
templates = Jinja2Templates(directory="app2/templates")


# connection = pymysql.connect(host='project-db-campus.smhrd.com', user='campus_25IS_health1_p2_3', password="smhrd3", db='campus_25IS_health1_p2_3', port=3307 ,charset='utf8')

# try:
#     with connection.cursor() as cursor:
#         sql = "select * from jetbot_move"
#         cursor.execute(sql)
#         result = cursor.fetchall()
        
# #         for i in result:
# #             print(i)
# except pymysql.MySQLError as e:
#     print(f"Database error occurred: {e}")
# except Exception as e:
#     print(f"An unexpected error occurred: {e}")            
# finally:
#     connection.close()
    
robot = Robot()    
RGB = Programing_RGB()
    

@app.get("/")
async def read_root(request:Request) : 
    return templates.TemplateResponse("test2.html", {"request": request, "message": request})

@app.get("/{order}")
async def read_root(order) : 
    if order=='start' :
        print(order)
        robot.forward(1)        
        return {'order':order}
    if order=='stop' :
        print(order)
        robot.stop()
        return {'order':order}
    if order=='desin' :
        print(order)
        RGB.OFF_ALL_RGB()
        time.sleep(3)
        RGB.Set_All_RGB(0xFF, 0x00, 0x00)
        return {'order':order}
    if order=='auto' :
        print(order)
#         스레드를 생성해서
        threading.Thread(target=worker, args=("스레드 1",)).start()
#         이미지를 만들고,
#         전송 이미지 결과 리턴
        return {'order':order}