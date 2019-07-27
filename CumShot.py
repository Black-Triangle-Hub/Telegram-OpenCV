from imutils.video import VideoStream
import argparse
import datetime
import imutils
import time
import cv2
import numpy as np
import re
import socks
import requests
import telethon
from telethon.tl.functions.contacts import ResolveUsernameRequest
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import GetFullChatRequest
from telethon.tl.types import InputChannel
from telethon import TelegramClient, events, sync
from telethon.tl.types import PeerUser, PeerChat, PeerChannel
from telethon.tl.types import InputPeerEmpty

api_id = 888888
api_hash = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
phone = "+7999999999"
chat = "black_triangle_tg"

client = TelegramClient('coma1', api_id, api_hash)
client.start()
client.sign_in(phone)

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
ap.add_argument("-a", "--min-area", type=int, default=500, help="minimum area size")
args = vars(ap.parse_args())

if args.get("video", None) is None:
	vs = VideoStream(src=0).start()
	time.sleep(2.0)

else:
	vs = cv2.VideoCapture(args["video"])

firstFrame = None
count = 0

while True:
	frame = vs.read()
	frame = frame if args.get("video", None) is None else frame[1]
	text = "Unoccupied"
	if frame is None:
		break
	frame = imutils.resize(frame, width=500)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (21, 21), 0)
	if firstFrame is None:
		firstFrame = gray
		continue
	frameDelta = cv2.absdiff(firstFrame, gray)
	thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
	thresh = cv2.dilate(thresh, None, iterations=2)
	cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
	for c in cnts:
		if cv2.contourArea(c) < args["min_area"]:
			continue
		(x, y, w, h) = cv2.boundingRect(c)
		cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
		text = "Occupied"
		count = count + 1
		cv2.imwrite("frame%d.jpg" % count, frame)
		destination_channel_username=chat
		entity=client.get_entity(destination_channel_username)
		client.send_file(entity=entity,file="frame%d.jpg" % count )
		time.sleep(1)
	if count == 20:
		break
	cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
	cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
		(10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
	cv2.imshow("Security Feed", frame)
	cv2.imshow("Thresh", thresh)
	cv2.imshow("Frame Delta", frameDelta)
	key = cv2.waitKey(1) & 0xFF
	if key == ord("q"):
		break
vs.stop() if args.get("video", None) is None else vs.release()
cv2.destroyAllWindows()
