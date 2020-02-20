from clipmanager import celery_app
import time
from celery import shared_task
import requests
import re
import urllib.request
import datetime

from blog.models import HighlightClip, Clip

import ffmpeg
import os
import shutil
import traceback

import sys

import socket
import socks


@shared_task
def sleepy(duration):
    print("Start Sleeping for ", duration, "secs")
    time.sleep(duration)
    print("I'm awake!")
    return None


@shared_task
def generate_thumbnail_task(id):
    # print(HighlightClip.objects.filter(id=id))
    # print(os.getcwd())
    highlight = HighlightClip.objects.filter(id=id)[0]
    (
        ffmpeg
            .input(highlight.path, ss=highlight.start_time)
            .filter('scale', 640, -1)
            .output(highlight.path + '.jpg', vframes=1)
            .run()
    )
    highlight = HighlightClip.objects.filter(id=id)[0]
    if os.path.exists(os.path.join(os.path.dirname(highlight.path), 'thumbnails')) == False:
        os.mkdir(os.path.join(os.path.dirname(highlight.path), 'thumbnails'))
    try:
        shutil.move(highlight.path + '.jpg', os.path.join(os.path.dirname(highlight.path), 'thumbnails'))
    except Exception as e:
        print('move_file ERROR: ', e)
        traceback.print_exc()

    highlight.thumbnail_path = os.path.join(os.path.dirname(highlight.path), 'thumbnails',
                                            os.path.basename(highlight.path) + '.jpg')

    highlight.save()
    return None


@shared_task
def encode_video(id):
    highlight = HighlightClip.objects.filter(id=id)[0]

    if highlight is not None:
        encode_path = os.path.join(os.path.dirname(os.path.dirname(highlight.path)), 'encoded')
        start_time = highlight.start_time
        duration = highlight.duration
        kbit = 7000
        video = ffmpeg.input(highlight.path, ss=start_time).video
        audio = ffmpeg.input(highlight.path, ss=start_time).audio
        (
            ffmpeg
                .output(video, audio, os.path.join(encode_path, 'encoded_' + os.path.basename(highlight.path)),
                        t=duration, vcodec='h264', f='mp4',
                        video_bitrate=kbit * 1000)
                .overwrite_output()
                .run()
        )
    # Encode需要时间，所以这里需要重新获取一下highlight对象
    highlight = HighlightClip.objects.filter(id=id)[0]
    # highlight.thumbnail_path = highlight.path + '.jpg'
    highlight.encode_complete = True
    os.remove(os.path.join(os.path.dirname(highlight.path), highlight.filename))
    encode_path = os.path.join(encode_path, 'encoded_' + os.path.basename(highlight.path))
    highlight.encoded_path = encode_path
    highlight.file_deleted = True
    highlight.thumbnail_path = os.path.join(os.path.dirname(highlight.path), 'thumbnails',
                                            os.path.basename(highlight.path) + '.jpg')

    highlight.save()
    return None


@shared_task
def download_clip():
    socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 10808)
    socket.socket = socks.socksocket

    basepath = 'downloads'
    base_clip_path = 'https://clips-media-assets2.twitch.tv/'
    cid = 'a9vim7vswasdr57nt3ote8t1pf1dq9'
    api_base = 'https://api.twitch.tv/kraken/clips/top'
    clips = Clip.objects.filter(downloaded=True)
    '''
        for item in clips:
        item.downloaded=False
        item.save()
    '''

    clips = Clip.objects.filter(accepted=True, downloaded=False)
    count = 0
    for clip in clips:
        print(clip.download_url)
        slug = clip.slug
        mp4_url = clip.download_url
        clip_title = clip.title
        regex = re.compile('[^a-zA-Z0-9_]')
        clip_title = clip_title.replace(' ', '_')
        out_filename = '[' + str(clip.views) + '-views]' + regex.sub('', clip_title) + '[' + str(
            clip.created_at.strftime("%Y-%m-%d")) + ']' + '.mp4'
        '''
                if os.path.exists(os.path.join(basepath, str(clip.created_at.strftime("%Y-%m-%d")))) == False:
            os.mkdir(os.path.join(basepath, clip.created_at.strftime("%Y-%m-%d")))
        # out_filename = regex.sub('', clip_title) + '.mp4'
        '''

        output_path = os.path.join(basepath, str(out_filename))
        # output_path = (basepath + out_filename)

        # print('out_filename:',out_filename)

        print('\n[DOWNLOAD CLIP]' + slug)
        print('"' + clip_title + '" -> ' + str(out_filename))
        # print(mp4_url)
        urllib.request.urlretrieve(mp4_url, output_path)
        print('No:', count, 'Done.\n')
        count += 1
        clip.downloaded = True
        clip.save()

    return 'All Accepted Video Are Downloaded!'
