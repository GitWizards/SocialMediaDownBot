import requests


class PinterestDownloader:
    def __init__(self):
        pass

    def get_url(self, url: str):
        try:
        
            headers = {

            'referer': 'https://pinterestdownloader.io/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            }

            response = requests.request("GET", f"https://pinterestdownloader.io/frontendService/DownloaderService?url={url}", headers=headers).json()
     
            caption = response['title']
            
            media_url = response['medias'][-1]['url']

            extension = "photo" if response['duration'] == None else "url"
            
            print(caption)
            print(media_url)
            print(extension)
            
        
            return media_url,  caption, extension
        

        except Exception as e:
            print(e)
            return None, None, "error"


            
            
