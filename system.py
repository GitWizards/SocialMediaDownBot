import json
import time
import requests
import os
from requests import *
from datetime import datetime
from config import *
from tiktok_module import downloaderTT
from instagram_module import downloaderIG

api = "https://api.telegram.org/bot" + token_bot
update_id = 0


def SendVideo(userid, msgid):
    tg_url = api + "/sendvideo"
    data = {
        "chat_id": userid,
        "reply_to_message_id": msgid,
    }
    res = post(
        tg_url,
        data=data,
        files={
            "video": open("video.mp4", "rb")
        }
    )


def SendMsg(userid, text, msgid):
    tg_url = api + "/sendmessage"
    post(
        tg_url,
        json={
            "chat_id": userid,
            "text": text,
            "parse_mode": "html",
            "reply_to_message_id": msgid
        }
    )


def get_time(tt):
    ttime = datetime.fromtimestamp(tt)
    return f"{ttime.hour}-{ttime.minute}-{ttime.second}-{ttime.day}-{ttime.month}-{ttime.year}"


def Bot(update):
    try:
        global last_use
        userid = update['message']['chat']['id']
        meseg = update['message']['text']
        msgid = update['message']['message_id']
        timee = update['message']['date']
        dl_tiktok = downloaderTT.tiktok_downloader()
        dl_instagram = downloaderIG.instagram_downloader()
        if update['message']['chat']['type'] != "private" and "tiktok.com" in meseg and "https://" in meseg or "http://" in meseg:
            getvid = dl_tiktok.musicaldown(url=meseg, output_name="video.mp4")
            if int(len(open('video.mp4', 'rb').read()) / 1024) > 51200:
                getvid = dl_tiktok.musicaldown(
                    url=meseg, output_name="video.mp4")
            SendVideo(
                userid,
                msgid
            )
            os.remove('video.mp4')
            return
        elif update['message']['chat']['type'] != "private" and "instagram.com/reel/" in meseg and "https://" in meseg or "http://" in meseg:
            getvid = dl_instagram.igram(url=meseg, output_name="video.mp4")
            if int(len(open('video.mp4', 'rb').read()) / 1024) > 51200:
                getvid = dl_instagram.igram(url=meseg, output_name="video.mp4")
            SendVideo(
                userid,
                msgid
            )
            os.remove('video.mp4')
            return
        first_name = update['message']['chat']['first_name']
        print(f"{get_time(timee)}-> {userid} - {first_name} -> {meseg}")
        if meseg.startswith('/start'):
            SendMsg(
                userid,
                "<b>Welcome to Tiktok Video Downlaoder Bot !</b>\n\n<b>How to use this bot </b>:\n<i>just send or paste url video tiktok on this bot </i>!!\n",
                msgid
            )
        elif "tiktok.com" in meseg and "https://" in meseg:
            getvid = dl_tiktok.musicaldown(url=meseg, output_name="video.mp4")
            if getvid == False:
                SendMsg(
                    userid,
                    "<i>Failed to download video</i>\n\n<i>Try again later</i>",
                    msgid
                )
                return
            elif getvid == "private/remove":
                SendMsg(
                    userid,
                    "<i>Failed to download video</i>\n\n<i>Video was private or removed</i>",
                    msgid
                )
            elif int(len(open('video.mp4', 'rb').read()) / 1024) > 51200:
                SendMsg(
                    userid,
                    "<i>Failed to download video</i>\n\n<i>Video size to large</i>",
                    msgid
                )
            elif getvid == 'url-invalid':
                SendMsg(
                    userid,
                    "<i>URL is invalid, send again !</i>",
                    msgid)
            else:
                SendVideo(
                    userid,
                    msgid
                )
                os.remove('video.mp4')
    except KeyError:
        return
