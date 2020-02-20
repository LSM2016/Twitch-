from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class AsyncTask(models.Model):
    id = models.BigAutoField(primary_key=True)


class Edit(models.Model):
    id = models.BigAutoField(primary_key=True)
    start_time = models.FloatField(default=0)
    duration = models.FloatField(default=0)

    def __str__(self):
        return self.id


class Channel(models.Model):
    name = models.CharField(max_length=256)
    display_name = models.CharField(max_length=256)
    channel_id = models.CharField(max_length=256)
    channel_url = models.CharField(max_length=1024)
    logo = models.CharField(max_length=2048)

    def __str__(self):
        return self.name


# Not Yet Implemented
class Cursor(models.Model):
    cursor = models.CharField(max_length=256)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    finished = models.BooleanField()

    def __str__(self):
        return self.cursor


class Clip(models.Model):
    title = models.CharField(max_length=1024)
    # slug是Twitch里面为每个clip生成的唯一string标签
    slug = models.CharField(max_length=1024)
    tracking_id = models.CharField(max_length=256)
    vod_id = models.CharField(max_length=256)
    vod_url = models.CharField(max_length=2048)
    vod_offset = models.IntegerField()
    vod_preview_img = models.CharField(max_length=2048)
    game = models.CharField(max_length=2048)
    views = models.IntegerField()
    duration = models.FloatField()
    created_at = models.DateTimeField()
    medium_thumbnail = models.CharField(max_length=2048)
    small_thumbnail = models.CharField(max_length=2048)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)

    reviewed = models.BooleanField(default=False, null=True)
    accepted = models.BooleanField(default=False, null=True)
    downloaded = models.BooleanField(default=False, null=True)
    rejected = models.BooleanField(default=False, null=True)

    download_url = models.CharField(max_length=2048, null=True)

    edit = models.ForeignKey(Edit, on_delete=models.CASCADE,null=True)

    def __str__(self):
        return self.title


class Vod(models.Model):
    name = models.CharField(max_length=1024)

    def __str__(self):
        return self.name


class HighlightClip(models.Model):
    title = models.CharField(max_length=2048)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='highlightclip', null=True)
    author = models.CharField(max_length=512)
    title = models.CharField(max_length=2048)

    filename = models.CharField(max_length=2048)
    path = models.CharField(max_length=2048)

    start_time = models.FloatField()
    duration = models.FloatField()

    upload_complete = models.BooleanField(default=True)
    encode_complete = models.BooleanField(default=False)
    file_deleted = models.BooleanField(default=False)

    clip_type = models.SmallIntegerField(default=0)

    clip_used = models.BooleanField(default=False, null=True)

    def __str__(self):
        return self.title



