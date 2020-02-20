from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
import os
import time
from .clipmanager import ClipManager
from .models import Channel, Clip, HighlightClip
import shutil
import traceback
from datetime import datetime
from clipmanager.tasks import generate_thumbnail_task, encode_video, download_clip


# Create your views here.
def videoplayer(request):
    url = request.GET.get('videourl')
    return render(request, 'blog/videoplayer.html', {'videourl': url})


def dashboard(response):
    return render(response, 'blog/base_admin.html')


def index(response):
    if response.user is not []:
        user = response.user
    return render(response, "blog/index.html", {'user': user})


def login(response):
    return render(response, "blog/login.html")


def submit_success(response):
    return render(response, 'blog/submit-success.html')


def submit(response):
    if response.user is not []:
        user = response.user
    # print(response.POST)
    # <QueryDict: {'csrfmiddlewaretoken': ['TyTMLhsydMTLShkiiE2VCBLQPRjME9bbEtdDN2qK87Q7NBSETC137bbpYHXUDGae'], 'start': ['0'], 'duration': ['5'], 'author': ['jack'], 'title': ['研发日志-人工智能编程'], 'target-filename': ['长身之处.mp4'], 'customRadioInline1': ['on']}>
    if response.POST.get('target-filename') is not None:
        target_filename = response.POST.get('target-filename')
        author = response.POST.get('author')
        title = response.POST.get('title')
        start = response.POST.get('start')
        duration = response.POST.get('duration')
        if response.POST.get('customRadioInline1') == 'on':
            cliptype = 0
        else:
            cliptype = 1
        clip_used = False

        user_path = os.path.join('upload', user.username)
        user_upload_path = os.path.join('upload', user.username, 'uploaded')
        user_encode_path = os.path.join('upload', user.username, 'encoded')
        if os.path.exists(user_path) == False:
            os.mkdir(user_path)
        if os.path.exists(user_upload_path) == False:
            os.mkdir(user_upload_path)
        if os.path.exists(user_encode_path) == False:
            os.mkdir(user_encode_path)
        path = os.path.join(user_upload_path, target_filename)
        upload_complete = True
        encode_complete = False
        file_deleted = False

        highlight = HighlightClip()

        highlight.user = user
        highlight.author = author
        highlight.title = title
        highlight.filename = target_filename
        highlight.path = path
        highlight.start_time = start
        highlight.duration = duration
        highlight.upload_complete = upload_complete
        highlight.encode_complete = encode_complete
        highlight.file_deleted = file_deleted
        highlight.clip_type = cliptype
        highlight.clip_used = clip_used

        highlight.save()
        return HttpResponseRedirect('submit_success', {'user': user})

    return render(response, "blog/submit.html", {'user': user})


def home(request):
    return HttpResponse('<h1>Home</h1>')


def about(request):
    return HttpResponse('<h1>About</h1>')


def ajax_macie(request):
    print(request.GET)
    if request.GET.get('action') is not None:
        action = request.GET.get('action')
        if request.GET.get('slug') is not None:
            slug = request.GET.get('slug')
            if action == 'accept':
                clip = Clip.objects.filter(slug=slug)[0]
                print('accepting ', clip.title)
                clip.reviewed = True
                clip.accepted = True
                clip.save()
            elif action == 'reject':
                clip = Clip.objects.filter(slug=slug)[0]
                print('rejecting ', clip.title)
                clip.reviewed = True
                clip.rejected = True
                clip.save()

    return HttpResponse('ok')
    # return render(request, 'ajax2.html')


def download_videos(request):
    download_clip.delay()
    return HttpResponse('<h1>Clips Download Started</h1>')


def macie(response):
    clips = []

    if response.POST.get('start') is not None:
        start = response.POST.get('start')
        start = str(start) + "-00:00:00"
        start_datetime = datetime.strptime(start, '%m/%d/%Y-%H:%M:%S')
        if response.POST.get('end') is not None:
            end = response.POST.get('end')
            end = str(end) + "-23:59:59"
            end_datetime = datetime.strptime(end, '%m/%d/%Y-%H:%M:%S')

            channel = Channel.objects.filter(name='maciejay')[0]

            clips = Clip.objects.filter(created_at__range=(start_datetime, end_datetime), rejected=False,
                                        accepted=False,channel=channel).order_by('-views')

    return render(response, 'blog/projects-grid-cards.html', {'clips': clips, 'review': True})


def update_clip_views(response):
    clips = []
    clips = Clip.objects.filter(reviewed=False, downloaded=False)
    clipmanager = ClipManager()
    count = 1
    total = len(clips)
    print("UPDATING VIEWS")
    for item in clips:
        item = clipmanager.update_clip_view(item)
        print("[UPDATE CLIP VIEWS]", count, ' of ', total)
        if item.views > 5:
            item.rejected = False
            item.accepted = False
            print("[New Commer!]")
        if item.views < 6:
            item.rejected = True
            print(count, ' has been REJECTED')
        item.save()
        count += 1
    return HttpResponse('<h1>所有直播的播放数已更新</h1>')


def macie_reviewed(response):
    clips = []

    if response.POST.get('start') is not None:
        start = response.POST.get('start')
        start = str(start) + "-00:00:00"
        start_datetime = datetime.strptime(start, '%m/%d/%Y-%H:%M:%S')
        if response.POST.get('end') is not None:
            end = response.POST.get('end')
            end = str(end) + "-23:59:59"
            end_datetime = datetime.strptime(end, '%m/%d/%Y-%H:%M:%S')

            channel = Channel.objects.filter(name='maciejay')[0]

            clips = Clip.objects.filter(created_at__range=(start_datetime, end_datetime), reviewed=True, rejected=False,
                                        accepted=True, downloaded=False,channel=channel)

    return render(response, 'blog/projects-grid-cards.html', {'clips': clips, 'review': False})


def macie_downloaded(response):
    clips = []

    if response.POST.get('start') is not None:
        start = response.POST.get('start')
        start = str(start) + "-00:00:00"
        start_datetime = datetime.strptime(start, '%m/%d/%Y-%H:%M:%S')
        if response.POST.get('end') is not None:
            end = response.POST.get('end')
            end = str(end) + "-23:59:59"
            end_datetime = datetime.strptime(end, '%m/%d/%Y-%H:%M:%S')

            clips = Clip.objects.filter(created_at__range=(start_datetime, end_datetime), reviewed=True, rejected=False,
                                        accepted=True, downloaded=True)

    return render(response, 'blog/projects-grid-cards.html', {'clips': clips, 'review': False})


def update_macie_twitch(request):
    clipmanager = ClipManager()
    clips = clipmanager.retrieve_clips_data(channel='maciejay', period='week', limit=100, cursor="")

    return HttpResponse('<h1>每周的直播片段已更新</h1>')


def update_macie_daily(request):
    clipmanager = ClipManager()
    clips = clipmanager.retrieve_clips_data(channel='maciejay', period='day', limit=30, cursor="")

    return HttpResponse('<h1>MacieJay\'s 每天的直播片段已更新</h1>')


def update_macie_all(request):
    clipmanager = ClipManager()
    try:
        clips = clipmanager.retrive_clips_by_count(channel='maciejay', period='all', limit=100, total_count=3000,
                                                   cursor="")
    except Exception as e:
        print(e)
    finally:
        clips = clipmanager.retrive_clips_by_count(channel='maciejay', period='all', limit=100, total_count=3000,
                                                   cursor="")

    return HttpResponse('<h1>MacieJay\'s 排名靠前5000的直播片段已更新</h1>')


def update_download_url(request):
    clips = Clip.objects.all()
    clipmanager = ClipManager()
    for item in clips:
        clipmanager.update_clip_url(item)
    return HttpResponse('<h1>所有直播片段的下载地址已更新</h1>')


def upload(request):
    return render(request, 'blog/upload.html')


@csrf_exempt
def upload_index(request):
    if request.method == 'POST':
        task = request.POST.get('task_id')  # 获取文件的唯一标识符
        chunk = request.POST.get('chunk', 0)  # 获取该分片在所有分片中的序号
        filename = '%s%s' % (task, chunk)  # 构造该分片的唯一标识符

        upload_file = request.FILES['file']
        with open('upload/%s' % filename, 'wb') as f:
            f.write(upload_file.read())
        print("upload ...")
    return HttpResponse('ok')


@csrf_exempt
def upload_complete(request):
    target_filename = request.GET.get('filename')  # 获取上传文件的文件名
    task = request.GET.get('task_id')  # 获取文件的唯一标识符
    user = request.GET.get('user')

    chunk = 0  # 分片序号
    print(target_filename, task)
    with open('upload/%s' % target_filename, 'wb') as target_file:  # 创建新文件
        while True:
            try:
                filename = 'upload/%s%d' % (task, chunk)
                source_file = open(filename, 'rb')  # 按序打开每个分片
                target_file.write(source_file.read())  # 读取分片内容写入新文件
                source_file.close()
            except IOError as msg:
                break
            chunk += 1
            os.remove(filename)  # 删除该分片，节约空间
    time.sleep(1)
    # 如果用户的文件夹不存在
    user_path = os.path.join('upload', user)
    user_upload_path = os.path.join('upload', user, 'uploaded')
    user_encode_path = os.path.join('upload', user, 'encoded')
    if os.path.exists(user_path) == False:
        os.mkdir(user_path)
    if os.path.exists(user_upload_path) == False:
        os.mkdir(user_upload_path)
    if os.path.exists(user_encode_path) == False:
        os.mkdir(user_encode_path)

    if os.path.exists(user_upload_path):
        try:
            if os.path.exists(os.path.join(user_upload_path, target_filename)):
                os.remove(os.path.join(user_upload_path, target_filename))
            shutil.move(os.path.join('upload', target_filename), user_upload_path)
        except Exception as e:
            print('move_file ERROR: ', e)
            traceback.print_exc()
    time.sleep(1)
    return render(request, "blog/index.html",
                  {'target_filename': target_filename, 'user_upload_path': user_upload_path})


def save_agent(f, username):
    # whether the existing is in tesing or validation
    path_valid = "validateAgent/" + username + "/"
    path_test = "testingAgent/" + username + "/"
    if os.path.exists(path_valid) or os.path.exists(path_test):
        return False
    path = 'uploadAgent/' + username + '.zip'
    print("start.....")
    with open(path, 'wb+') as destination:
        print("open safely")
        for chunk in f.chunks():
            destination.write(chunk)
    print("submit finished!")
    return True
