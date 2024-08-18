import requests
import re
import json


class InstagramDownloader:

    def __init__(self):
        pass

    def get_instagram_post_id(self, media_id: str):
        post_id = ""
        try:
            # Split the mediaId by '_' and take the first part, then convert to integer
            id = int(media_id.split("_")[0])
            alphabet = (
                "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
            )

            while id > 0:
                remainder = id % 64
                id = id // 64  # Use floor division to ensure an integer result
                post_id = alphabet[remainder] + post_id
        except Exception as e:
            print(e)

        return post_id

    """
    def estrai_identificativo_da_link(self, link: str):
        # Espressione regolare per identificare il tipo di link e estrarre l'identificativo
        regex_stories = r"/stories/[^/]+/(\d+)/?$"
        regex_reel = r"/reel/([^/?]+)/\??"
        regex_post = r"/p/([^/?]+)/\??"

        # Cerca corrispondenze nelle stringhe del link
        match_stories = re.search(regex_stories, link)
        match_reel = re.search(regex_reel, link)
        match_post = re.search(regex_post, link)

        # Se trova corrispondenze, restituisce l'identificativo corrispondente
        if match_stories:
            return self.get_instagram_post_id(match_stories.group(1))
        elif match_reel:
            return match_reel.group(1)
        elif match_post:
            return match_post.group(1)
        else:
            return None
    """

    def get_url(self, url: str):

        payload = json.dumps({"url": f"{url}"})

        link = "https://fastdl.app/api/convert"
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7,es;q=0.6,zh-CN;q=0.5,zh;q=0.4",
            "content-type": "application/json",
            "origin": "https://fastdl.app",
            "priority": "u=1, i",
            "referer": "https://fastdl.app/it",
            "sec-ch-ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        }

        try:
            resp = requests.post(link, headers=headers, data=payload).json()
            
            if len(resp["url"]) >= 3:
                download_link = resp["url"][1]["url"]
            else:
                download_link = resp["url"][0]["url"]
                
            type_url = "url"

            caption = resp["meta"]["title"]
            if ".mp4" in caption or "stories" in caption:
                caption = ""

            return download_link, caption, type_url
        except:
            print("Failed to open {}".format(link))
            return None, None, "error"
