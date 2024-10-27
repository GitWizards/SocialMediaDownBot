import requests
import re

class InstagramDownloader:

    def __init__(self):
        pass
    
    
    def get_media_data_by_media_id(self,video_id: str) -> tuple:
        ig_query_url = "https://www.instagram.com/graphql/query"

        payload = {
            "variables": '{"shortcode":"' + video_id + '"}',
            "doc_id": "8845758582119845",
        }

        response = requests.post(ig_query_url, data=payload)
        response_json = response.json()


        if response_json.get("data", {}).get("xdt_shortcode_media"):
            #media = response_json["data"]["xdt_shortcode_media"]
            type_media = ''
            document = []
        
            if not response_json["data"]["xdt_shortcode_media"].get("is_video", ""):
                video_url = response_json["data"]["xdt_shortcode_media"].get("thumbnail_src", "")
                type_media = "image"
            else:
                video_url = response_json["data"]["xdt_shortcode_media"].get("video_url", "")
                type_media = "video"
                

            if "video" in type_media:
                video_url = response_json["data"]["xdt_shortcode_media"].get("video_url", "")
            else:
                video_url = response_json["data"]["xdt_shortcode_media"].get("thumbnail_src", "")
                
            try:
                video_description = response_json["data"]["xdt_shortcode_media"]["edge_media_to_caption"]["edges"][0]["node"].get("text", "")
            except IndexError:
                video_description = ""

            
            try:
                album = response_json["data"]["xdt_shortcode_media"]['edge_sidecar_to_children']['edges']
                type_media = "album"
                

                for i in range(0, len(album)):
                    document.append(response_json["data"]["xdt_shortcode_media"]['edge_sidecar_to_children']['edges'][i]['node']['display_url'])

                return document, video_description, 'media'
            except:
                pass
            

            #video_duration = response_json["data"]["xdt_shortcode_media"].get("video_duration", 0)
            
            

            return video_url, video_description, type_media

        return "error", "error"

    def get_video_id_from_url(self,url: str) -> str:
        video_id_pattern = r"https:\/\/www\.instagram\.com(?:[_0-9a-z.\/]+)?\/reel\/(.+)\/"
        match = re.search(video_id_pattern, url)
        if match:
            return match.group(1)  # Restituisce il primo ID video trovato
        return ""  # Restituisce una stringa vuota se non trova match
    
    def get_photo_id_from_url(self,url: str) -> str:
        photo_id_pattern = r"https:\/\/www\.instagram\.com(?:[_0-9a-z.\/]+)?\/p\/(.+)\/"
        match = re.search(photo_id_pattern, url)
        if match:
            return match.group(1)  # Restituisce il primo ID video trovato
        return ""  # Restituisce una stringa vuota se non trova match



    def get_url(self, url: str):
        
        try:
            
            if 'reel' in url:
                media_id = self.get_video_id_from_url(url)
            else:
                media_id = self.get_photo_id_from_url(url)
                
            
                
            #print(media_id)
                
            download_link, caption, type_media = self.get_media_data_by_media_id(media_id)
            
            if 'album' in type_media:
                return download_link, caption, "url"
            else:
                return download_link, caption, "media"
                
                
        except:
    
            return None, None, "error"