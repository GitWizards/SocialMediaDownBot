import json
import os
import queue
import random
import string
import threading
import requests
from PIL import Image
from requests import head
from resizer_module import Resizer

class TikTokDownloader:
    
    
    def __init__(self):
        pass

    async def get_url(self, url_tiktok):

        url = "https://www.tikwm.com/api/"
        params = {
            "url": url_tiktok,
            "count": 12,
            "cursor": 0,
            "web": 1,
            "hd": 1
        }

        headers = {
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        }


        response = requests.request("POST", url, headers=headers, data=params).text

        data = json.loads(response, strict=False)
        
        music_url = ''
        album = ''
        
        if data['code'] == 0:
            try:
                if len(data['data']['images']):
                    caption = data['data']['title']
                    video_type = 'album'
                    music_url =  "https://www.tikwm.com" +data['data']['music']
                    response = requests.get(music_url)
                    music_url = response.url
                    album = data['data']['images']
            except:
                    video_type = 'video'
                
            if video_type == "video":
                video_name = "https://www.tikwm.com" +data['data']['play']
                file_size  = head(video_name,allow_redirects=True)
                size = file_size.headers.get('Content-Length')
                caption = data['data']['title']
                if len(caption) > 1000:
                    caption = caption[:997]+ '...'
                    
                if int(size) / 1000000 <= 21:
                    response = requests.get(video_name)
                    final_url = response.url
                    return final_url, caption, 'url'
                else:
                    resizer = Resizer()
                    q = queue.Queue()
                    threading.Thread(
                        target=resizer.resize,
                        args=(video_name, q)
                    ).start()
                    result = q.get()

                    return result, caption, 'mp4'
            
            
            
            elif video_type == "album":

                r = requests.get(music_url)
                with open(f"{os.getcwd()}/audio.m4a", 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:  # filter out keep-alive new chunks
                            f.write(chunk)

                array_album = []
                for i in range(len(album)):
                    array_album.append(album[i])


                return array_album, caption, 'media'
        else:
            return None, None, "error"


def random_name(size=6, chars=string.ascii_uppercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size)) + ".mp4"
