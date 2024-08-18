import asyncio
import logging
import os
import re
import warnings
import requests
from random import randrange
import csv
import moviepy.editor as mp
from config import TOKEN
from facebook_module import FacebookDownloader
from instagram_module import InstagramDownloader
from pid.decorator import pidfile
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      InlineQueryResultPhoto, InlineQueryResultVideo,
                      InputMediaPhoto, InputMediaVideo, Update)
from telegram.ext import (CallbackQueryHandler, CommandHandler, Filters,
                          InlineQueryHandler, MessageHandler, Updater,
                          run_async)
from tiktok_module import TikTokDownloader
from twitter_module import TweetDownloader
from youtube_module import ShortsDownloader
from threads_module import ThreadsDownloader
from pinterest_module import PinterestDownloader

warnings.filterwarnings("ignore")

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)
name_raw = ''

def startHandler(update: Update, _):
    update.message.reply_text(
        "Welcome to *Media Downloader Bot!*\n\n"
        "Send me a link to download the media.\n"
        "Supported sites:\n- TikTok\n- Instagram reels\n- Facebook\n- YouTube Shorts",
        parse_mode="Markdown",
    )

def write_csv (name,message_user,chat_id):
    existing_data = []
    # Scrive i dati nel file CSV
    with open('backup.csv', 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            existing_data.append(row)
            
    new_data = [name, message_user, chat_id]
    existing_data.append(new_data)
            
    with open('backup.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(existing_data)


@run_async
def linkHandler(update: Update, _):
    message_user = re.search(
        "(?P<url>https?://[^\s]+)", str(update.message.text)).group("url")
    type_message = len(update.message.text) - len(message_user)
    if type_message == 0:
        quote_message = False
    else:
        quote_message = True
        
    chat_id = update.message.chat_id
    name = update.message.from_user.username
    name_raw = name
    if name == None:
        name = update.message.from_user.first_name
        name_raw = name
        


        

    # If the Bot is on a group enter the words 'Sent by @'
    if update.message.chat.type == "supergroup":
        name = f"Inviato da [@{name}](tg://user?id={update.message.from_user.id})"
    else:
        name = ''

    inverted = False

    if message_user[-2:] == "_i":
        message_user = message_user[:-2]
        inverted = True

    # Generate a random number, if it is 5 change the InlineKeyboardButton
    if randrange(10) != 5:
        keyboard = [[InlineKeyboardButton("🔗🌐", url=message_user)]]
    else:
        keyboard = [[InlineKeyboardButton("🧧", url='https://paypal.me/radeox'),
                     InlineKeyboardButton("🔗🌐", url=message_user)

                     ]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    # TikTok Media
    if "tiktok.com" in message_user:
        write_csv (name_raw,message_user, chat_id)

        print(f'From TikTok --> {message_user}')
        tt_downloader = TikTokDownloader()
        if inverted:
            url, caption, type_link = asyncio.run(
                tt_downloader.get_url(message_user+'_i'))
        else:
            url, caption, type_link = asyncio.run(
                tt_downloader.get_url(message_user))

        if type_link == 'mp4':
            clip = mp.VideoFileClip(url)
            duration = clip.duration
            update.message.reply_video(
                quote=quote_message,
                video=open(url, "rb"),
                timeout=10000,
                parse_mode="Markdown",
                caption=filter_caption(name, caption, "TT"),
                height=clip.size[1],
                width=clip.size[0],
                duration=str(duration), reply_markup=reply_markup
            )
            delete_file(url)
        elif type_link == 'url':
            update.message.reply_video(
                quote=quote_message,
                timeout=10000,
                video=url,
                caption=filter_caption(name, caption, "TT"),
                parse_mode="Markdown", reply_markup=reply_markup)
        elif type_link == "error":
            update.message.reply_text(
                quote=quote_message,
                text="*Video or picture of private*\n\n",
                parse_mode="Markdown", reply_markup=reply_markup
            )

        # Delete old message
        if type_message == 0:
            update.message.delete()

    # Threads Media
    elif "threads.net" in message_user:
        write_csv (name_raw,message_user, chat_id)

        print(f'From Threads --> {message_user}')
        tr_downloader = ThreadsDownloader()
        url, caption, type_link = tr_downloader.get_url(message_user)
        
        if type_link == 'photo':
            update.message.reply_photo(
                quote=quote_message,
                photo=url,
                caption=filter_caption(name, caption, "TS"),
                parse_mode="Markdown", reply_markup=reply_markup
            )
        
        elif type_link == 'url':
            update.message.reply_video(
                quote=quote_message,
                video=url,
                timeout=10000,
                caption=filter_caption(name, caption, "TS"),
                parse_mode="Markdown", reply_markup=reply_markup
            )
            
        elif type_link == 'media':
            try:
                media_group = []
                for i in range(len(url)):
                    if 'image' in url[i] or 'webp' in url[i]:
                        media_type = InputMediaPhoto
                    else:
                        media_type = InputMediaVideo

                    
                    if i == 0:
                        media_group.append(media_type(media=requests.get(url[i]).content, caption=filter_caption(
                            name, caption, "TS"), parse_mode="Markdown"))
                    else:
                        media_group.append(media_type(media=requests.get(url[i]).content))
            except:
                pass

            update.message.reply_media_group(
                timeout=10000,
                quote=quote_message,
                media=media_group
            )
            
        elif type_link == "error":
            update.message.reply_text(
                quote=quote_message,
                text="*Photo/Video not exists or private*\n\n",
                parse_mode="Markdown", reply_markup=reply_markup
            )
            
        # Delete old message
        if type_message == 0:
            update.message.delete()
            
            
     # Pinterest Media
    elif "pinterest.com" in message_user or "pin." in message_user:
        write_csv (name_raw,message_user, chat_id)

        print(f'From Pinterest --> {message_user}')
        pr_downloader = PinterestDownloader()
        url, caption, type_link = pr_downloader.get_url(message_user)
        
        if type_link == 'photo':
            update.message.reply_photo(
                quote=quote_message,
                photo=url,
                caption=filter_caption(name, caption, "TS"),
                parse_mode="Markdown", reply_markup=reply_markup
            )
        
        elif type_link == 'url':
            update.message.reply_video(
                quote=quote_message,
                video=url,
                timeout=10000,
                caption=filter_caption(name, caption, "TS"),
                parse_mode="Markdown", reply_markup=reply_markup
            )
        elif type_link == "error":
            update.message.reply_text(
                quote=quote_message,
                text="*Photo/Video not exists or private*\n\n",
                parse_mode="Markdown", reply_markup=reply_markup
            )
            
        # Delete old message
        if type_message == 0:
            update.message.delete()

    # Instagram Media
    elif "instagram.com/" in message_user:
        write_csv (name_raw,message_user, chat_id)

        print(f'From Instagram --> {message_user}')
        # Get video URL and send it
        dl_instagram = InstagramDownloader()
        url, caption, type_link = dl_instagram.get_url(message_user)

        if type_link == 'photo':
            update.message.reply_photo(
                quote=quote_message,
                photo=url,
                caption=filter_caption(name, caption, "IG"),
                parse_mode="Markdown", reply_markup=reply_markup
            )

        elif type_link == 'url':
            update.message.reply_video(
                quote=quote_message,
                video=url,
                timeout=10000,
                caption=filter_caption(name, caption, "IG"),
                parse_mode="Markdown", reply_markup=reply_markup
            )

        elif type_link == 'mp4':
            clip = mp.VideoFileClip(url)
            duration = clip.duration
            update.message.reply_video(
                quote=quote_message,
                video=open(url, "rb"),
                timeout=10000,
                parse_mode="Markdown",
                caption=filter_caption(name, caption, "IG"),
                height=clip.size[1],
                width=clip.size[0],
                duration=str(duration), reply_markup=reply_markup
            )
            delete_file(url)

        elif type_link == 'album':

            try:
                media_group = []
                for i in range(len(url)):
                    if 'mp4' in url[i]:
                        media_type = InputMediaVideo
                    else:
                        media_type = InputMediaPhoto

                    if i == 0:
                        media_group.append(media_type(media=url[i], caption=filter_caption(
                            name, caption, "IG"), parse_mode="Markdown"))
                    else:
                        media_group.append(media_type(media=url[i]))
            except:
                pass

            update.message.reply_media_group(
                timeout=10000,
                quote=quote_message,
                media=media_group
            )

        elif type_link == "error":
            update.message.reply_text(
                quote=quote_message,
                text="*Photo/Video not exists or private*\n\n",
                parse_mode="Markdown", reply_markup=reply_markup
            )

        # Delete old message
        if type_message == 0:
            update.message.delete()

    # Facebook
    elif (
        "facebook.com/share/" in message_user or
        "facebook.com/reel/" in message_user or
        ("facebook" in message_user and "video" in message_user)
    ):
        write_csv (name_raw,message_user, chat_id)

        print(f'From Facebook --> {message_user}')
        # Get video URL and send it
        dl_fb = FacebookDownloader()
        url, caption, type_link = dl_fb.get_url(message_user)

        if type_link == 'url':
            update.message.reply_video(
                quote=quote_message,
                timeout=10000,
                video=url,
                caption=filter_caption(name, caption, "FB"),
                parse_mode="Markdown", reply_markup=reply_markup)

        elif type_link == "error":
            update.message.reply_text(
                quote=quote_message,
                text="*Photo/Video not exists or private*\n\n",
                parse_mode="Markdown", reply_markup=reply_markup
            )
            
        # Delete old message
        if type_message == 0:
            update.message.delete()
            
    # YouTube Shorts
    elif "youtube.com/shorts/" in message_user:
        write_csv (name_raw,message_user, chat_id)

        print(f'From YouTube --> {message_user}')
        # Get video URL and send it
        ys_downloader = ShortsDownloader()
        url, caption, type_link = ys_downloader.get_url(message_user)

        if type_link == "url":
            update.message.reply_video(
                quote=quote_message,
                timeout=10000,
                video=url,
                caption=filter_caption(name, caption, "YT"),
                parse_mode="Markdown", reply_markup=reply_markup)

        elif type_link == "error":
            update.message.reply_text(
                quote=quote_message,
                text="*Video or picture of private*\n\n",
                parse_mode="Markdown", reply_markup=reply_markup
            )
        # Delete old message
        if type_message == 0:
            update.message.delete()

    

    # Iwantu
    elif "x.com" in message_user or "twitter.com" in message_user:
        write_csv (name_raw,message_user, chat_id)

        print(f'From Twitter --> {message_user}')
        # Get video URL and send it
        twitter_downloader = TweetDownloader()
        url, caption, type_link = twitter_downloader.get_url(
            message_user)

        if type_link == 'message':
            update.message.reply_text(
                filter_caption(name, caption, "X"),
                parse_mode="Markdown", reply_markup=reply_markup
            )

        elif type_link == 'url':
            update.message.reply_video(
                quote=quote_message,
                timeout=10000,
                video=url,
                caption=filter_caption(name, caption, "X"),
                parse_mode="Markdown", reply_markup=reply_markup)
            
        elif type_link == 'photo':
            update.message.reply_photo(
                quote=quote_message,
                photo=url,
                caption=filter_caption(name, caption, "X"),
                parse_mode="Markdown", reply_markup=reply_markup
            )

        elif type_link == 'album':

            try:
                media_group = []
                for i in range(len(url)):
                    if 'mp4' in url[i]:
                        media_type = InputMediaVideo
                    else:
                        media_type = InputMediaPhoto

                    if i == 0:
                        media_group.append(media_type(media=url[i], caption=filter_caption(
                            name, caption, "X"), parse_mode="Markdown"))
                    else:
                        media_group.append(media_type(media=url[i]))
            except:
                pass

            update.message.reply_media_group(
                timeout=10000,
                quote=quote_message,
                media=media_group
            )

        elif type_link == "error":
            update.message.reply_text(
                quote=quote_message,
                text="*Photo/Video not exists or private*\n\n",
                parse_mode="Markdown", reply_markup=reply_markup
            )

        # Delete old message
        if type_message == 0:
            update.message.delete()



def button(update: Update, _):
    query = update.callback_query.data
    query.answer()


def filter_caption(name, caption, social):

    caption = re.sub("\s*\B#\w+(?:\s*#\w+)*\s*$", "", caption)
    caption = re.sub("#", "", caption)

    if social == "TT":
        link_account = "https://www.tiktok.com/@"
    elif social == "IG":
        link_account = "https://www.instagram.com/"
    elif social == "YT":
        link_account = "https://www.youtube.com/user/"
    elif social == "FB":
        link_account = "https://www.facebook.com/user/"
    elif social == "X":
        link_account = "https://twitter.com/"
    elif social == "TS":
        link_account = "https://www.threads.net/"

    caption = re.sub(r'@(\w+)', f'[@\\1]({link_account}\\1)', caption)

    #caption = caption.replace("_", "\_")
    #caption = caption.replace("*", "\*")

    return f"{name}\n\n{caption}"


def delete_file(mp4File):
    os.remove(mp4File)
    try:
        get_file = os.listdir(os.getcwd() + "/")

        for item in get_file:
            if item.endswith(".png"):
                os.remove(os.path.join(os.getcwd() + "/", item))
    except:
        pass


def loadUrlInline(message_user):

    # TikTok
    if "tiktok.com" in message_user:
        # Get video URL and send it
        tt_downloader = TikTokDownloader()
        url, caption, type_link = asyncio.run(
            tt_downloader.get_url(message_user))
        if type_link != 'mp4':
            return InlineQueryResultVideo(id='url', title=caption, video_url=url, thumb_url=url, mime_type='video/mp4', caption=filter_caption('', caption, "TT"), parse_mode="Markdown")

    # Instagram video/photo/stories
    elif "instagram.com" in message_user:
        dl_instagram = InstagramDownloader()
        url, caption, type = dl_instagram.get_url(message_user)
        if type == "photo":
            return InlineQueryResultPhoto(id='url', title="Invia Url", photo_url=url, thumb_url=url)
        if type == "video":
            return InlineQueryResultVideo(id='url', title="Invia Url", video_url=url, thumb_url=url, mime_type='video/mp4', caption=filter_caption('', caption, "IG"), parse_mode="Markdown")

    # Facebook
    elif (
        "facebook.com/reel/" in message_user or
        "watch" in message_user or
        ("facebook" in message_user and "video" in message_user)
    ):
        # Get video URL and send it
        dl_fb = FacebookDownloader()
        url, caption = dl_fb.get_url(message_user)
        if url != None:
            return InlineQueryResultVideo(id='url', title=caption, video_url=url, thumb_url=url, mime_type='video/mp4', caption=filter_caption('', caption, "FB"), parse_mode="Markdown")

    '''
    # YouTube Shorts
    elif "youtube.com/shorts/" in message_user:
        # Get video URL and send it
        ys_downloader = ShortsDownloader()
        url, caption, thumbnail_url = ys_downloader.get_url(message_user)
        return InlineQueryResultVideo(id='url', title=caption, video_url=url, thumb_url=thumbnail_url, mime_type='video/mp4', caption=filter_caption('', caption, "YT"), parse_mode="Markdown")
    '''


def inline_query(update: Update, _) -> None:
    query = update.inline_query.query

    if query == "":
        return

    results = [
        loadUrlInline(query)
    ]
    try:
        update.inline_query.answer(results)
    except AttributeError:
        pass


@ pidfile('/tmp/SocialMediaDownlaoder.pid')
def main():
    print("--- Starting Social Media Downloader Bot ---")
    # Setup bot
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Add handlers
    dispatcher.add_handler(CommandHandler("start", startHandler))
    dispatcher.add_handler(MessageHandler(
        Filters.regex(r"http.?://"), linkHandler))
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(InlineQueryHandler(inline_query))

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
