import requests
import re
import html


class ThreadsDownloader:

    def __init__(self):
        pass

    def get_url(self, url_threads):
        retries = 0
        url_threads = re.sub(r'\?.*$', '', url_threads)  # Rimuove query string dall'URL

        while retries < 5:
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

            try:
                response = requests.post(
                    "https://videothreadsdownloader.com/wp-admin/admin-ajax.php",
                    headers=headers,
                    data=payload,
                    timeout=10  # Timeout per evitare blocchi
                )
                data = response.json()
            except requests.RequestException:
                retries += 1
                continue  # Riprova in caso di errore di rete
            except ValueError:
                return None, None, "error"  # Errore di parsing JSON

            # Gestione delle risposte HTTP
            if data.get("code") == 200:
                data_items = data.get("data", [])
                caption = self.get_description(url_threads)
                
                video_not_found = False  # Questa variabile può essere definita in base alla logica

                if video_not_found:
                    media_url = self.get_video(url_threads)
                    return media_url, caption, "media"

                links = [item["url"] for item in data_items if "url" in item]
                
                
                if len(links) == 1:
                    if "jpg" in links[0] or "webp" in links[0]:
                        return requests.get(links[0]).content, caption, "photo"
                    else:
                        return requests.get(links[0]).content, caption, "url"

                if len(links) > 1:
                    return links, caption, "media"

            elif data.get("code") == 500:
                retries += 1  # Incrementa i tentativi in caso di errore server

            else:
                return None, None, "error"

        return None, None, "error"  # Dopo 5 tentativi falliti

    def get_video(self, url_threads):
        headers = {
            "origin": "https://sssthreads.pro",
            "referer": "https://sssthreads.pro/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        }

        response = requests.get(
            f"https://api.threadsphotodownloader.com/v2/media?url={url_threads}",
            headers=headers,
        )

        data = response.json()
        url_media_array = []

        if len(data["image_urls"]) == 1:
            url_media_array.append(data["image_urls"][0])
        url_media_array.append(data["video_urls"][0]["download_url"])

        return url_media_array

    def get_description(self, url_threads):
        response = requests.get(url_threads)
        html_content = response.text

        # Cerca il contenuto del tag meta con l'attributo property="og:description"
        description_match = re.search(
            r'<meta\s+property="og:description"\s+content="([^"]*)"', html_content
        )

        if description_match:
            description = html.unescape(description_match.group(1)).replace("_", "\\_")
            return description
        
        return ""  # Restituisce una stringa vuota se non trovata
