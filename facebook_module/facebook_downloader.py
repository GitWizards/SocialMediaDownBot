import json
import re
import requests
from resizer_module import Resizer
import html

class FacebookDownloader:
    def __init__(self):
        pass
    
    def generate_id(self, url: str):
        video_id = ''
        if url.isdigit():
            video_id = url
        else:
            match = re.search(r'(\d+)/?$', url)
            if match:
                video_id = match.group(1)
        return video_id

    def clean_str(self, s: str):
        return json.loads('{"text": "%s"}' % s)['text']

    def get_sd_link(self, content: str):
        regex_rate_limit = r'browser_native_sd_url":"([^"]+)"'
        match = re.search(regex_rate_limit, content)
        if match:
            return self.clean_str(match.group(1))
        else:
            return False


    def get_description(self, content: str):
        match = re.search(r'<meta name="description" content="([^"]*)" />', content)
        if match:
            return ' '.join(match.group(1).split('. ')[:-1])
        
        return False

    def get_url(self, url: str):
        try:
            headers = {
                'sec-fetch-user': '?1',
                'sec-ch-ua-mobile': '?0',
                'sec-fetch-site': 'none',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'cache-control': 'max-age=0',
                'authority': 'www.facebook.com',
                'upgrade-insecure-requests': '1',
                'accept-language': 'en-GB,en;q=0.9,tr-TR;q=0.8,tr;q=0.7,en-US;q=0.6',
                'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
            }

            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            content = response.text

     
            sd_link = self.get_sd_link(content)
            
            if not sd_link:
                return None, None, "error"
            try:
                caption = html.unescape(self.get_description(content))
            except:
                caption = ''
            return sd_link,  caption, 'url'

        except Exception as e:
            print(e)
            return None, None, "error"

            
            
        '''
            title = bs4.BeautifulSoup(r.text, features="html.parser")
            caption = f"{title.title.text.split(' | ')[0]}\n\n{title.title.text.split(' | ')[1]}"
            if len(a) == 0:
                print("\033[1;31;40m[!] Video Not Found...")
                return None, None, 'error'
            else:
                link_video = unquote(r.text.split("?src=")[1].split('"')[0])

                response = head(link_video)
                size = response.headers["content-length"]
                print(str(int(size) / 1000000))
                if int(size) / 1000000 <= 21:
                    return link_video, caption, 'url'
                else:
                    resizer = Resizer()
                    q = queue.Queue()
                    threading.Thread(
                        target=resizer.resize,
                        args=(link_video, q)
                    ).start()
                    result = q.get()

                    return result, caption, 'mp4'
        '''

