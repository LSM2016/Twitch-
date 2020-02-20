import re
import urllib.request
import requests
import sys
from .models import Channel, Clip
import datetime

import socket
import socks

import time


class ClipManager:
    def __init__(self):
        self.basepath = 'downloads/'
        self.base_clip_path = 'https://clips-media-assets2.twitch.tv/'
        self.cid = '填入你的APPID'
        self.api_base = 'https://api.twitch.tv/kraken/clips/top'

    def retrieve_clips_data(self, channel, period, limit, cursor):
        socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 10808)
        socket.socket = socks.socksocket

        header = {"Client-ID": self.cid,
                  "Accept": 'application/vnd.twitchtv.v5+json'}
        if cursor != "":
            request_url = self.api_base + '?channel=' + str(channel) + '&period=' + str(period) + '&limit=' + str(
                limit) + '&cursor=' + str(cursor)
        else:
            request_url = self.api_base + '?channel=' + str(channel) + '&period=' + str(period) + '&limit=' + str(limit)
        response = requests.get(request_url, headers=header).json()
        clips_data = response['clips']
        cursor = response['_cursor']

        channel = Channel()
        channel_data = clips_data[0]['broadcaster']

        print('[API Resnponse]' + str(clips_data))
        print('[Total Clips Data Received]'+str(len(clips_data)))
        # 检查该频道信息是否已存在
        check_channel = Channel.objects.filter(channel_id=channel_data['id'])
        if len(check_channel) == 0:
            channel.name = channel_data['name']
            channel.display_name = channel_data['display_name']
            channel.channel_id = channel_data['id']
            channel.channel_url = channel_data['channel_url']
            channel.logo = channel_data['logo']
            channel.save()

        else:
            channel = check_channel[0]

        clips = []
        for item in clips_data:
            check_clip = Clip.objects.filter(slug=item['slug'])
            if len(check_clip) == 0:
                clip = Clip()
                clip_data = item
                print(item)
                # channel外键
                clip.channel = channel
                clip.slug = clip_data['slug']
                clip.title = clip_data['title']
                clip.tracking_id = clip_data['tracking_id']

                print('[Clip Not Exist]'+str(clip.slug))

                try:
                    clip.vod_id = clip_data['vod']['id']
                    clip.vod_offset = int(clip_data['vod']['offset'])
                    clip.vod_url = clip_data['vod']['url']
                    clip.vod_preview_img = clip_data['vod']['preview_image_url']
                except Exception as e:
                    print(e)
                finally:
                    clip.vod_id = ""
                    clip.vod_offset = 0
                    clip.vod_url = ""
                    clip.vod_preview_img = ""

                clip.game = clip_data['game']
                clip.views = int(clip_data['views'])
                if clip.views < 6:
                    clip.reviewed = True
                    clip.rejected = True
                clip.duration = float(clip_data['duration'])
                # "created_at": "2020-01-04T20:12:04Z",
                clip.created_at = datetime.datetime.strptime(clip_data['created_at'], '%Y-%m-%dT%H:%M:%SZ')
                print(clip.created_at)
                clip.medium_thumbnail = clip_data['thumbnails']['medium']
                clip.small_thumbnail = clip_data['thumbnails']['small']
                '''
                 clip_info = requests.get(
                    "https://api.twitch.tv/helix/clips?id=" + clip.slug,
                    headers={"Client-ID": self.cid}).json()
                print('[Clip_info]'+str(clip_info))
                '''

                thumb_url = clip_data['thumbnails']['small']
                title = clip_data['title']
                slice_point = thumb_url.index("-preview-")
                mp4_url = thumb_url[:slice_point] + '.mp4'

                clip.download_url = mp4_url
                clip.save()
            else:
                clip = check_clip[0]
                print('[Clip Exist]')
            clips.append(clip)
        return clips, cursor

    def retrive_clips_by_count(self, total_count, channel, period, limit, cursor):
        count = 0
        clips = []
        cursor = ""

        while count < total_count:
            print('[Update Clips]' + str(count))
            if count == 0:
                clips_tmp, cursor = self.retrieve_clips_data(channel, period, limit, cursor)
            else:
                clips_tmp, cursor = self.retrieve_clips_data(channel, period, limit, cursor)
            count += limit
            clips.append(clips_tmp)

            print('[Sleep]Sleep for 2.5s')
            time.sleep(2.5)

        return clips

    def update_clip_url(self, clip):
        socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 10808)
        socket.socket = socks.socksocket

        clip_info = requests.get(
            "https://api.twitch.tv/helix/clips?id=" + clip.slug,
            headers={"Client-ID": self.cid}).json()
        thumb_url = clip_info['data'][0]['thumbnail_url']
        title = clip_info['data'][0]['title']
        slice_point = thumb_url.index("-preview-")
        mp4_url = thumb_url[:slice_point] + '.mp4'
        clip.download_url = mp4_url
        print(clip.download_url)
        clip.save()
        return clip

    def update_clip_view(self, clip):
        socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 10808)
        socket.socket = socks.socksocket

        clip_info = requests.get(
            "https://api.twitch.tv/helix/clips?id=" + clip.slug,
            headers={"Client-ID": self.cid}).json()
        # print(clip_info)
        clip.views = int(clip_info['data'][0]['view_count'])
        # print(clip.views)
        clip.save()
        return clip


def retrieve_mp4_data(slug):
    socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 10808)
    socket.socket = socks.socksocket

    cid = sys.argv[1]
    clip_info = requests.get(
        "https://api.twitch.tv/helix/clips?id=" + slug,
        headers={"Client-ID": cid}).json()
    thumb_url = clip_info['data'][0]['thumbnail_url']
    title = clip_info['data'][0]['title']
    slice_point = thumb_url.index("-preview-")
    mp4_url = thumb_url[:slice_point] + '.mp4'
    return mp4_url, title
