
import re

import requests


class TweetDownloader:
    def __init__(self):
        pass

    def get_url(self, url):

        url = url.replace('x.com', 'twitter.com').split('?')[0]
        extracted_number = url.split(".com/")[1]

        headers = {
            'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
            'Referer': 'https://platform.twitter.com/',
            'sec-ch-ua-mobile': '?0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
            'sec-ch-ua-platform': '"Windows"'
        }

        response = requests.get(
            f'https://api.fxtwitter.com/{extracted_number}', headers=headers)

        if response.status_code == 200:
            data = response.json()
            if data.get("message") == "OK":
  
                caption = data['tweet']['text']
            
                try:
                    download_link = data['tweet']['media']['videos'][0]['url']
                    caption = re.sub(r'https://t\.co/\w+', '', caption)
                    return download_link, caption, 'url'
                except:
                    try:
                        if len(data['tweet']['media']['photos']) == 1:
                            array_photo = data['tweet']['media']['photos'][0]['url']
                            return array_photo, caption, 'photo'
                        else:
                            array_photo = []
                            for i in range(len(data['tweet']['media']['photos'])):
                                array_photo.append(
                                    data['tweet']['media']['photos'][i]['url'])

                            caption = f"{caption}\n\n[Visualizza Tweet]({url})"
                            return array_photo, caption, 'album'
                    except:
                        return None, caption, 'message'                    
            else:
                return None, caption, 'message'
        elif response.status_code == 404:
            return None, None, 'error'
