import re
import socket
from base64 import b16decode
from distutils.log import log
from tkinter import S
from tkinter.messagebox import NO
from typing_extensions import dataclass_transform
from unicodedata import category
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.urls import reverse
from django.db.models import Q
from django.contrib.auth.hashers import check_password
from django.core.paginator import Paginator
from .models import Post, Comment, MyUser, PostRecommend, CommentRecommend

from post.utils import substring, get_user
    

def index(request):
    
    def get_posts_by_category(category):
        return Post.objects.filter(category="잡담", notice=0).order_by("-time")
    
    post1 = request.POST.get('post1', "")
    post2 = request.POST.get('post2', "")
    post3 = request.POST.get('post3', "")
    post_list = []    
        
    if(bool(post1)):
        post_list = get_posts_by_category('잡담')
    elif(bool(post2)):
        post_list = Post.objects.filter(category="공부", notice=0).order_by("-time")
    elif(bool(post3)):
        post_list = Post.objects.filter(category="운동", notice=0).order_by("-time")
    else:
        post_list = Post.objects.filter(notice=0).order_by("-time")
        
        
    select_category = request.GET.get('select_category')
    if(select_category == "recently"):
        post_list = Post.objects.all().order_by("-time")
    elif(select_category == "views"):
        post_list = Post.objects.all().order_by("-views")
    elif(select_category == "likes"):
        post_list = Post.objects.all().order_by("-recommendation")
        
        
    search = request.POST.get('search', "")
    my_list = ""
    
    if(search != ""):
        
        
        a = Post.objects.filter(contents__icontains=search)
        if(my_list == ""):
            my_list = a
        
        b = Post.objects.filter(nickname__icontains=search)
            
        if(my_list == ""):
            my_list = b
        else:
            my_list = my_list.union(b)
        
        c = Post.objects.filter(title__icontains=search)
            
        if(my_list == ""):
            my_list = c
        else:
            my_list = my_list.union(c)
        
        post_list = my_list
            
    
    for i in post_list:
        if len(i.title) > 40:
            i.title = i.title[0:40] + '...'
        if len(i.nickname) > 5:
            i.nickname = i.nickname[0:5] + '...'
            
    
    paginator = Paginator(post_list, 10)
    page = int(request.GET.get('page', 1))
    list = paginator.get_page(page)
    
    user = request.session.get('login_session')
    nickname = ""
    
    if(user is not None):
        myuser = MyUser.objects.get(userid=user)
        nickname = myuser.nickname
        
        
    user = get_user(request)
    if user is not None:
        nickname = substring(user.nickname)
        
    if len(nickname) > 10:
        nickname = nickname[0:10] + '...'
    
    notice_post_list = Post.objects.filter(notice=1).order_by("-time")
    
    count = post_list.count() + notice_post_list.count()
    
    return render(request, 'post/index.html', {'post_list':list, 'search':search, 'count':count,
                                               'nickname':nickname, 'notice_post_list':notice_post_list})

# 회원가입
def signup(request):
    return render(request, 'post/signup.html')

def signup_hill(request):
    userid = request.POST['userid']
    pw = request.POST['pw']
    repw = request.POST['repw']
    name = request.POST['name']
    email = request.POST['email']
    nickname = request.POST['nickname']
    error = 1
    errorid = ""
    errorpw = ""
    errorrepw = ""
    errorname = ""
    erroremail = ""
    errornickname = ""
    
    # 아이디 검사
    if(userid == ""):
        errorid = "아이디를 입력해주세요."
        error = 0
    else:
        korean = re.compile('[\u3131-\u3163\uac00-\ud7a3]+')
        a = re.sub(korean, '', userid)
        a = re.sub('[A-Z]', '', a)
        a = re.sub(r'[^\uAC00-\uD7A30-9a-zA-Z\s]', '', a)
        
        
        if(a != userid):
            errorid = "5에서 50자 이내의 영문 소문자, 숫자만 사용 가능합니다."
            error = 0
        elif(len(userid) < 5 or len(userid) > 50):
            errorid = "5에서 50자 이내의 영문 소문자, 숫자만 사용 가능합니다."
            error = 0
            
    # 비밀번호 검사
    if(pw == ""):
        errorpw = "비밀번호를 입력해주세요."
        error = 0
    else:
        korean = re.compile('[\u3131-\u3163\uac00-\ud7a3]+')
        a = re.sub(korean, '', pw)
        a = re.sub('[A-Z]', '', a)
        a = re.sub('[-=+,/\?:.\"※~ㆍ』\\‘|\(\)\[\]\<\>`\'…》]', '', a)
        b = re.sub('[a-z]', '', pw)
        c = re.sub('[0-9]', '', pw)
        d = re.sub('[!@#$%^&*]', '', pw)
        
        if(a != pw):
            errorpw = "8에서 50자 이내의 영문 소문자, 숫자, 특수문자( !, @, #, $, %, ^, &, *)만 사용 가능합니다."
            error = 0
        elif(len(pw) < 8 or len(pw) > 50):
            errorpw = "8에서 50자 이내의 영문 소문자, 숫자, 특수문자( !, @, #, $, %, ^, &, *)만 사용 가능합니다."
            error = 0
        elif(pw == b):
            errorpw = "5에서 50자 이내에서 영문 소문자와 숫자, 특수문자( !, @, #, $, %, ^, &, *)를 함께 사용해야합니다."
            error = 0
        elif(pw == c):
            errorpw = "5에서 50자 이내에서 영문 소문자와 숫자, 특수문자( !, @, #, $, %, ^, &, *)를 함께 사용해야합니다."
            error = 0
        elif(pw == d):
            errorpw = "5에서 50자 이내에서 영문 소문자와 숫자, 특수문자( !, @, #, $, %, ^, &, *)를 함께 사용해야합니다."
            error = 0
            
    # 비밀번호 재확인 검사
    if(repw == ""):
        errorrepw = "비밀번호 재확인 칸을 입력해주세요."
        error = 0
    if(pw != repw):
        errorrepw = "비밀번호를 다시 확인해주세요."
        error = 0
        
    # 이름 검사
    if(name == ""):
        errorname = "이름을 입력해주세요."
        error = 0
    else:
        a = re.sub('[0-9]', '', name)
        a = re.sub('[-=+,/\!@#$%^&*?:.\"※~ㆍ』\\‘|\(\)\[\]\<\>`\'…》]', '', a)
        
        if(a != name):
            errorname = "2에서 50자 이내의 영문 소문자, 영문 대문자, 한글만 사용 가능합니다."
            error = 0
        elif(len(name) < 2 or len(name) > 50):
            errorname = "2에서 50자 이내의 영문 소문자, 영문 대문자, 한글만 사용 가능합니다."
            error = 0
        
    # 이메일 검사
    if(email == ""):
        erroremail = "이메일을 입력해주세요."
        error = 0
    else:
        a = re.compile('([A-Za-z]+[A-Za-z0-9]+@[A-Za-z]+\.[A-Za-z]+)')
        b = a.search(email.replace(" ", ""))
        
        if not b:
            erroremail = "이메일을 확인해주세요."
            error = 0
        
    # 활동명 검사
    if(nickname == ""):
        errornickname = "활동명을 입력해주세요."
        error = 0
    else:
        a = re.sub('[-=+,/\!@#$%^&*?:.\"※~ㆍ』\\‘|\(\)\[\]\<\>`\'…》]', '', nickname)
        
        if(a != nickname):
            errornickname = "2에서 50자 이내의 영문 소문자, 영문 대문자, 한글, 숫자만 사용 가능합니다."
            error = 0
        elif(len(nickname) < 2 or len(nickname) > 50):
            errornickname = "2에서 50자 이내의 영문 소문자, 영문 대문자, 한글, 숫자만 사용 가능합니다."
            error = 0
        
    if error:
        try:
            a = MyUser.objects.get(userid=userid)
            errorid = "현재 사용중인 아이디입니다."
            userid = ""
        except MyUser.DoesNotExist:
            try:
                a = MyUser.objects.get(email=email)
                erroremail = "현재 사용중인 이메일입니다."
                email = ""
            except MyUser.DoesNotExist:
                a = MyUser(userid=userid, pw=pw,
                    name=name, email=email, 
                    nickname=nickname)
                a.save()
                
                return HttpResponseRedirect(reverse('post:index'))
    
    return render(request, 'post/signup.html', {'errorid':errorid, 'errorpw':errorpw, 'errorrepw':errorrepw,
                                                'errorname':errorname, 'erroremail':erroremail, 
                                                'errornickname':errornickname, 'userid':userid, 'pw':pw, 
                                                'repw':repw, 'name':name, 'email':email, 'nickname':nickname, })

# 로그인
def login(request):
    return render(request, 'post/login.html')

def login_hill(request):

    userid = request.POST.get('userid')
    pw = request.POST.get('pw')
    error = 1
    errorid = ""
    errorpw = ""
    
    # 아이디 검사
    if(userid == ""):
        errorid = "아이디를 입력해주세요."
        error = 0
            
    # 비밀번호 검사
    if(pw == ""):
        errorpw = "비밀번호를 입력해주세요."
        error = 0
           
    if error:
        try:
            a = MyUser.objects.get(userid=userid)
            if (a.pw == pw):
                request.session['login_session']=userid
                request.session.set_expiry(0)
                return HttpResponseRedirect(reverse('post:index'))
            else:
                errorpw = "비밀번호가 틀렸습니다."
                pw = ""
        except MyUser.DoesNotExist:
            errorid = "존재하지않는 아이디입니다."
            userid = ""
            
                
    
    return render(request, 'post/login.html', {'errorid':errorid, 'errorpw':errorpw, 
                                                'userid':userid, 'pw':pw})

# 로그아웃
def logout(request):
    request.session.flush()
    return HttpResponseRedirect(reverse('post:index'))
    


# 글쓰기
def write(request): 
    return render(request, 'post/write.html')

def write_post(request):
    notice = False
    contents=request.POST['contents']
    title=request.POST['title']
    category=request.POST['category']
    
    a = request.session.get('login_session')
    
    if a == None:
        Post(
            nickname=request.POST['nickname'], 
            title=title,
            contents=contents, 
            time=timezone.now(), 
            category=category, 
            pw=request.POST['pw'],
            notice=notice
        ).save()
        return HttpResponseRedirect(reverse('post:index'))
    
    user = MyUser.objects.get(userid=request.session.get('login_session'))

    if(user.userid == 'admin'):
        if(request.POST['notice'] == 'yes'):
            notice = True
    
    Post.objects.create(
        nickname=user.nickname, 
        title=title,
        contents=contents, 
        time=timezone.now(), 
        category=category, 
        pw=user.pw,
        notice=notice
    )
    
    return HttpResponseRedirect(reverse('post:index'))

# 게시글 클릭
def detail(request, post_id):
    post = Post.objects.get(num=post_id).readed()
    
    all_comment = Comment.objects.filter(Q(reply_id=post_id))
    count = all_comment.count()
    
    line = 44 + (post.contents.count('\n')) * 22
    
    post1 = request.POST.get('post1', "")
    post2 = request.POST.get('post2', "")
    post3 = request.POST.get('post3', "")
    
    select_category = request.GET.get('select_category')
    search = request.POST.get('search', "")
    
    post_list = ""
    
    if(post1 != ""):
        post_list = Post.objects.filter(category="잡담", notice=0).order_by("-time")
    elif(post2 !=""):
        post_list = Post.objects.filter(category="공부", notice=0).order_by("-time")
    elif(post3 !=""):
        post_list = Post.objects.filter(category="운동", notice=0).order_by("-time")
    else:
        post_list = Post.objects.filter(notice=0).order_by("-time")
    
    select_category = request.GET.get('select_category')
    if(select_category == "recently"):
        post_list = Post.objects.all().order_by("-time")
    elif(select_category == "views"):
        post_list = Post.objects.all().order_by("-views")
    elif(select_category == "likes"):
        post_list = Post.objects.all().order_by("-recommendation")
    
    search = request.POST.get('search', "")    
    my_list = ""
    
    if(search != ""):
        
        a = Post.objects.filter(Q(contents__icontains=search))
        if(my_list == ""):
            my_list = a
        
        b = Post.objects.filter(Q(nickname__icontains=search))
            
        if(my_list == ""):
            my_list = b
        else:
            my_list = my_list.union(b)
        
        c = Post.objects.filter(Q(title__icontains=search))
            
        if(my_list == ""):
            my_list = c
        else:
            my_list = my_list.union(c)
        
        post_list = my_list
    
    for i in post_list:
        if len(i.title) > 40:
            i.title = i.title[0:40] + '...'
        if len(i.nickname) > 5:
            i.nickname = i.nickname[0:5] + '...'
    
    paginator = Paginator(post_list, 10)
    page = int(request.GET.get('page', 1))
    list = paginator.get_page(page)
    
    user = request.session.get('login_session')
    nickname = ""
    
    
    if(user != None):
        myuser = MyUser.objects.get(userid=user)
        nickname = myuser.nickname
        
    if len(nickname) > 10:
        nickname = nickname[0:10] + '...'
    
    notice_post_list = Post.objects.filter(notice=1).order_by("-time")
    
    postcount = post_list.count() + notice_post_list.count()
    
    return render(request, 'post/detail.html', {'post': post, 'comment_list': all_comment, 
                                                'count':count, 'post_list':list, 'line':line,
                                                'nickname':nickname, 'search':search, 'postcount':postcount,
                                                'notice_post_list':notice_post_list})

# 게시글 추천
def post_recommend(request, post_id):
    nickname = ""
    if request.session.get('login_session') == None:
        nickname = "Unknown"
    else:
        user = MyUser.objects.get(userid=request.session.get('login_session'))
        nickname=user.nickname
        
    # ip = socket.gethostbyname(socket.gethostname())
    # error = ""
    # try:
    #     a = PostRecommend.objects.get(nickname=nickname)
    #     error = "중복하여 추천할 수 없습니다."
        
    # except MyUser.DoesNotExist:
    #     try:
    #         a = PostRecommend.objects.get(ip=ip)
    #         error = "중복하여 추천할 수 없습니다."
            
    #     except MyUser.DoesNotExist:
    #         a = PostRecommend(num=post_id, ip=ip, nickname=nickname)
    #         a.save()
    #         b=Post.objects.get(num=post_id)
    #         b.recommendation = b.recommendation + 1
    #         b.save()
    #         return HttpResponseRedirect(reverse('post:detail', args=(post_id,)))
    
    ip = socket.gethostbyname(socket.gethostname())
    post = Post.objects.get(num=post_id)
    a = PostRecommend(reply=post, ip=ip, nickname=nickname)
    a.save()
    
    post.recommendation = post.recommendation + 1
    post.views = post.views - 1
    post.save()
    
    return HttpResponseRedirect(reverse('post:detail', args=(post_id,)))

# 게시글 삭제
def remove_post(request, post_id):
    return render(request, 'post/remove_post.html', {'post_id':post_id})

def remove_post_check(request, post_id):
    pw = request.POST['pw']
    errorpw = ""
            
    # 비밀번호 검사
    if(pw == ""):
        errorpw = "비밀번호를 입력해주세요."
        return render(request, 'post/remove_post.html', {'errorpw':errorpw, 'post_id':post_id})
    
    a = Post.objects.get(num=post_id)
    
    if(a.pw != pw):
        errorpw = "비밀번호가 틀렸습니다."
        return render(request, 'post/remove_post.html', {'errorpw':errorpw, 'post_id':post_id})
    
    a.delete()
    
    return HttpResponseRedirect(reverse('post:index'))

# 게시글 수정
def re_post(request, post_id):
    return render(request, 'post/re_post.html', {'post_id':post_id})

def re_write(request, post_id):
    pw = request.POST['pw']
    errorpw = ""
            
    # 비밀번호 검사
    if(pw == ""):
        errorpw = "비밀번호를 입력해주세요."
        return render(request, 'post/re_post.html', {'errorpw':errorpw, 'post_id':post_id})
    
    post = Post.objects.get(num=post_id)
    
    if(post.pw != pw):
        errorpw = "비밀번호가 틀렸습니다."
        return render(request, 'post/re_post.html', {'errorpw':errorpw, 'post_id':post_id})
    
    return render(request, 'post/re_write.html', {'post_id':post_id, 'post':post})

def re_write_ok(request, post_id):
    notice = False
    contents=request.POST['contents']
    title=request.POST['title']
    category=request.POST['category']
    
    a = request.session.get('login_session')
    
    if a == None:
        post = Post.objects.get(num=post_id)
        post.title = title
        post.contents = contents
        post.category = category
        post.save()
        return HttpResponseRedirect(reverse('post:index'))
    
    user = MyUser.objects.get(userid=request.session.get('login_session'))
        
    if(user.userid == 'admin'):
        if(request.POST['notice'] == 'yes'):
            notice = True
    
    post = Post.objects.get(num=post_id)
    post.title = title
    post.contents = contents
    post.category = category
    post.notice = notice
    post.save()
    
    return HttpResponseRedirect(reverse('post:index'))



# 댓글 쓰기
def create_reply(request, post_id):
    a = Post.objects.get(num=post_id)
    a.views = a.views - 1
    a.save()
    i = request.session.get('login_session')
    nickname = ""
    pw = ""
    contents = request.POST['contents']
    
    if i == None:
        nickname = request.POST['comment_id']
        pw = request.POST['comment_pw']
    else:
        user = MyUser.objects.get(userid=i)
        nickname = user.nickname
        pw = user.pw
    
    b = Comment(reply=a, 
    nickname=nickname, 
    contents=contents, 
    pw=pw)
    b.save()
    return HttpResponseRedirect(reverse('post:detail', args=(post_id,)))

# 댓글 추천
def comment_recommend(request, comment_id, post_id):
    nickname = ""
    if request.session.get('login_session') == None:
        nickname = "Unknown"
    else:
        user = MyUser.objects.get(userid=request.session.get('login_session'))
        nickname=user.nickname
        
    # ip = socket.gethostbyname(socket.gethostname())
    # error = ""
    # try:
    #     a = PostRecommend.objects.get(nickname=nickname)
    #     error = "중복하여 추천할 수 없습니다."
        
    # except MyUser.DoesNotExist:
    #     try:
    #         a = PostRecommend.objects.get(ip=ip)
    #         error = "중복하여 추천할 수 없습니다."
            
    #     except MyUser.DoesNotExist:
    #         a = PostRecommend(num=post_id, ip=ip, nickname=nickname)
    #         a.save()
    #         b=Post.objects.get(num=post_id)
    #         b.recommendation = b.recommendation + 1
    #         b.save()
    #         return HttpResponseRedirect(reverse('post:detail', args=(post_id,)))
    
    ip = socket.gethostbyname(socket.gethostname())
    c = Comment.objects.get(num=comment_id)
    a = CommentRecommend(reply=c, ip=ip, nickname=nickname)
    a.save()
    
    b=Post.objects.get(num=post_id)
    b.views = b.views - 1
    b.save()
    
    c.recommendation = c.recommendation + 1
    c.save()
    
    return HttpResponseRedirect(reverse('post:detail', args=(post_id,)))

# 댓글 삭제
def remove_comment(request, comment_id, post_id):
    return render(request, 'post/remove_comment.html', {'post_id':post_id, 'comment_id':comment_id})

def remove_comment_check(request, comment_id, post_id):
    pw = request.POST['pw']
    errorpw = ""
            
    # 비밀번호 검사
    if(pw == ""):
        errorpw = "비밀번호를 입력해주세요."
        return render(request, 'post/remove_comment.html', 
                      {'errorpw':errorpw, 'post_id':post_id, 'comment_id':comment_id})
    
    a = Comment.objects.get(num=comment_id)
    
    if(a.pw != pw):
        errorpw = "비밀번호가 틀렸습니다."
        return render(request, 'post/remove_comment.html', 
                      {'errorpw':errorpw, 'post_id':post_id, 'comment_id':comment_id})
    
    a.delete()
    
    b=Post.objects.get(num=post_id)
    b.views = b.views - 1
    b.save()
    
    return HttpResponseRedirect(reverse('post:detail', args=(post_id,)))

# 댓글 수정
def re_comment(request, comment_id, post_id):
    return render(request, 'post/re_comment.html', {'comment_id':comment_id, 'post_id':post_id})

def re_comment_write(request, comment_id, post_id):
    pw = request.POST['pw']
    errorpw = ""
            
    # 비밀번호 검사
    if(pw == ""):
        errorpw = "비밀번호를 입력해주세요."
        return render(request, 'post/re_comment.html', {'errorpw':errorpw, 'comment_id':comment_id, 'post_id':post_id})
    
    comment = Comment.objects.get(num=comment_id)
    
    if(comment.pw != pw):
        errorpw = "비밀번호가 틀렸습니다."
        return render(request, 'post/re_comment.html', {'errorpw':errorpw, 'comment_id':comment_id, 'post_id':post_id})
    
    comment = Comment.objects.get(num=comment_id)
    
    return render(request, 'post/re_comment_write.html', {'comment_id':comment_id, 'post_id':post_id, 
                                                          'comment':comment})

def re_comment_write_ok(request, comment_id, post_id):
    a = Comment.objects.get(num=comment_id)
    contents = request.POST['contents']
    a.contents = contents
    a.save()
    
    b=Post.objects.get(num=post_id)
    b.views = b.views - 1
    b.save()
    
    return HttpResponseRedirect(reverse('post:detail', args=(post_id,)))

