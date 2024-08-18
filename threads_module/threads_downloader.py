import requests
import re
import html


class ThreadsDownloader:

    def __init__(self):
        pass

    def get_url(self, url_threads):

        payload = {
            "action": "threads_action",
            "threads": f"threads_video_url={url_threads}",
        }

        headers = {
            "origin": "https://videothreadsdownloader.com",
            "referer": "https://videothreadsdownloader.com/threads-scaricatore-di-video-immagini-gif/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
        }

        response = requests.request(
            "POST",
            "https://videothreadsdownloader.com/wp-admin/admin-ajax.php",
            headers=headers,
            data=payload,
        )

        data = response.json()

        # print(data)
        if data["success"]:
            data_items = data["data"]
            caption = self.get_description(url_threads)

            video_not_found = False
            for item in data_items:
                if item["type"] == "Video" and item["type"] == "Image":
                    if "url" not in item:
                        video_not_found = True

            if video_not_found:
                media_url = self.get_video(url_threads, video_not_found)
                return media_url, caption, "media"
            else:
                try:
                    links = [item["url"] for item in data_items]
                except:
                    links = [item["url"] for item in data_items if "url" in item]

                if len(links) == 0:
                    media_url = self.get_video(url_threads, video_not_found)
                    return media_url, caption, "url"

                if len(links) == 1:
                    if "image" in links[0]:
                        return requests.get(links[0]).content, caption, "photo"
                    else:
                        return requests.get(links[0]).content, caption, "url"
                if len(links) > 1:
                    return links, caption, "media"

        else:
            return None, None, "error"

    def get_video(self, url_threads, video_not_found):

        headers = {
            "origin": "https://sssthreads.pro",
            "referer": "https://sssthreads.pro/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        }

        response = requests.request(
            "GET",
            f"https://api.threadsphotodownloader.com/v2/media?url={url_threads}",
            headers=headers,
        )

        data = response.json()
        # print(data)

        url_media_array = []
        if video_not_found:
            if len(data["image_urls"]) == 1:
                url_media_array.append(data["image_urls"][0])
            url_media_array.append(data["video_urls"][0]["download_url"])

            return url_media_array
        else:
            url_media = requests.get(data["video_urls"][0]["download_url"]).content
            return url_media

    def get_description(self, url_threads):
        response = requests.get(url_threads)
        html_content = response.text

        # Cerca il contenuto del tag meta con l'attributo property="og:description"
        description_match = re.search(
            r'<meta\s+property="og:description"\s+content="([^"]*)"', html_content
        )

        if description_match:
            description = html.unescape(description_match.group(1))
            return description
        else:
            return ""
