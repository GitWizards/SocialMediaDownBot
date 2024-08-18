import json
import os
import queue
import random
import string
import threading
import ast
import cv2
import requests
from aiotiktok import TikTokClient
from moviepy.editor import AudioFileClip, CompositeAudioClip, VideoFileClip
from moviepy.video.fx import colorx
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

                largest = 0
                new_width = 0
                new_height = 0
                old_size = 0
                for i in range(len(album)):
                    url = album[i]

                    img_data = requests.get(url).content
                    with open(f"{os.getcwd()}/{i+10}.png", "wb") as handler:
                        handler.write(img_data)
                        width, height = Image.open(
                                f"{os.getcwd()}/{i+10}.png").size

                        if width*height > largest:
                                largest = width*height
                                new_width = width
                                new_height = height

                for i in range(len(album)):

                    old_im = Image.open(f"{os.getcwd()}/{i+10}.png")
                    old_size = old_im.size
                    new_size = (new_width, new_height)
                    new_im = Image.new(
                            "RGB", new_size, "Black"
                        )
                    box = tuple((n - o) // 2 for n,
                                    o in zip(new_size, old_size))
                    new_im.paste(old_im, box)
                    new_im.save(f"{os.getcwd()}/{i+10}.png")

                return generate_video_from_images(len(album)), caption, 'mp4'
        else:
            return None, None, "error"

def generate_video_from_images(len_photo):
    folder = f"{os.getcwd()}/"
    video_name = random_name()
    os.chdir(folder)

    audio = AudioFileClip(f"{folder}audio.m4a")
    duration_audio = audio.duration

    images = [img for img in os.listdir('.') if img.endswith("png")]
    images = sorted([int(num.split(".")[0]) for num in images])
    images = [f"{str(i)}.png" for i in images]

    fourcc = cv2.VideoWriter_fourcc("m", "p", "4", "v")
    frame = cv2.imread(os.path.join('.', images[0]))
    height, width, shape = frame.shape
    video = cv2.VideoWriter(video_name, fourcc, round(
        len_photo/duration_audio, 2), (width, height))

    for image in images:
        video.write(cv2.imread(os.path.join('.', image)))

    cv2.destroyAllWindows()
    video.release()

    videoclip = VideoFileClip(folder + video_name)
    duration_full_video = duration_audio

    audioclip = AudioFileClip(f"{folder}audio.m4a").subclip(
        0, duration_full_video)
    new_audioclip = CompositeAudioClip([audioclip])
    videoclip.audio = new_audioclip
    videoclip.write_videofile(
        folder + video_name, logger=None
    )

    return folder + video_name



def random_name(size=6, chars=string.ascii_uppercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size)) + ".mp4"
