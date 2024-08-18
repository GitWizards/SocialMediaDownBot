import os
import random
import string
import shutil
from requests import get
import moviepy.editor as mp


class Resizer:
    def __init__(self):
        return

    def resize(self, url, q):
        input_file = random_name()
        output_file = random_name()

        download_file(url, input_file)

        clip = mp.VideoFileClip(input_file)
        clip_resized = clip.resize(height=clip.size[0] / 1.25)
        clip_resized.write_videofile(
            output_file,
            threads=4,
            logger=None, verbose=False
        )

        clip = mp.VideoFileClip(output_file)

        q.put(output_file)
        os.remove(f"{os.getcwd()}/{input_file}")


def random_name(size=6, chars=string.ascii_uppercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size)) + ".mp4"


def download_file(url, input_file):
    with get(url, stream=True) as r:
        with open(input_file, "wb") as f:
            shutil.copyfileobj(r.raw, f)

    return input_file
