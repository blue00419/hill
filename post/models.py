from unittest.util import _MAX_LENGTH
from django.db import models
from post.utils import substring

# Create your models here.

class MyUser(models.Model):

    userid = models.CharField(max_length=50)                    # 로그인 아이디
    pw = models.CharField(max_length=50)                    # 로그인 비밀번호
    name = models.CharField(max_length=100)                 # 사용자 이름
    email = models.CharField(max_length=100)                # 본인 인증 용 이메일
    nickname = models.CharField(max_length=50)              # 활동명
    admin = models.BooleanField(default=False)
    # photo = models.CharField(max_length=300)                # 프로필 사진

    def get_nickname(self, length=10):
        return substring(self.nickname, length)

    def __str__(self):
        return self.pw

class Post(models.Model):

    num = models.AutoField(primary_key=True)                # 게시글 식별코드
    nickname = models.CharField(max_length=50)              # 게시자
    title = models.CharField(max_length=100)                # 제목
    contents = models.CharField(max_length=500)             # 내용
    time = models.DateTimeField()                           # 시간
    views = models.PositiveIntegerField(default=0)          # 방문자 수
    recommendation = models.PositiveIntegerField(default=0) # 추천 수
    category = models.CharField(max_length=20)              # 게시판 종류
    pw = models.CharField(max_length=50)                    # 비밀번호
    notice = models.BooleanField(default=False)                 # 공지on,off
    # photo
    
    def readed(self):
        self.views += 1
        self.save()
        return self
    
    def is_owner(self, user=None, nickname=None, password=None):
        
        assert user is not None, 'user 값은 필수입니다.'
        
        if user is not None:
            pass
        elif nickname is not None and password is not None:
            pass
        else:
            return False
    
    def get_comment(id):
        pass
    
    def get_comments(self):
        comment = Comment.objects.filter(reply_id=self.num)
        return comment, comment.count()
    
    def add_comments(conetns, user):
        pass

    def __str__(self):
        return self.title

class Comment(models.Model):

    reply = models.ForeignKey(Post, on_delete=models.CASCADE) # comment -> post 연결관계
    
    num = models.AutoField(primary_key=True)                # 댓글 식별코드
    nickname = models.CharField(max_length=50)              # 댓글 게시자
    contents = models.CharField(max_length=200)             # 내용
    time = models.DateTimeField(auto_now_add=True)                           # 시간
    recommendation = models.PositiveIntegerField(default=0) # 추천 수
    pw = models.CharField(max_length=50)                    # 비밀번호

    def __str__(self):
        return self.contents
    
class PostRecommend(models.Model):
    reply = models.ForeignKey(Post, on_delete=models.CASCADE) # postrecommend -> post 연결관계
    ip = models.CharField(max_length=20, default="")                    # 추천인 ip 주소
    nickname = models.CharField(max_length=50)              # 추천인 닉네임
    
    def __str__(self):
        return self.nickname
    
class CommentRecommend(models.Model):
    reply = models.ForeignKey(Comment, on_delete=models.CASCADE) # commentrecommend -> comment 연결관계
    ip = models.CharField(max_length=20, default="")                    # 추천인 ip 주소
    nickname = models.CharField(max_length=50)              # 추천인 닉네임
    
    def __str__(self):
        return self.nickname