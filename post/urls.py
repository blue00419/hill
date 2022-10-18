from django. urls import path

from . import views

app_name = 'post'
urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'), # 회원가입 창 이동
    path('signup_hill/', views.signup_hill, name='signup_hill'), # 회원가입

    path('login/', views.login, name='login'), # 로그인 창 이동
    path('login_hill/', views.login_hill, name='login_hill'), # 로그인
    path('logout/', views.logout, name='logout'), # 로그아웃
    
    path('write/', views.write, name='write'), # 글쓰기 창 이동
    path('write/write_post', views.write_post, name='write_post'), # 게시글 등록

    path('detail/<int:post_id>/', views.detail, name = 'detail'), # 게시글 창 이동
    path('detail/<int:post_id>/post_recommend/', views.post_recommend, name = 'post_recommend'), # 게시글 추천
    
    path('remove_post/<int:post_id>/', views.remove_post, name = 'remove_post'), # 게시글 삭제 확인
    path('remove_post_check/<int:post_id>/', views.remove_post_check, name = 'remove_post_check'), # 게시글 삭제
    
    path('re_post/<int:post_id>/', views.re_post, name = 're_post'), # 게시글 수정 확인
    path('re_write/<int:post_id>/', views.re_write, name = 're_write'), # 게시글 수정
    path('re_write_ok/<int:post_id>/', views.re_write_ok, name = 're_write_ok'), # 게시글 수정 완료
    
    path('<int:post_id>/create_reply', views.create_reply, name='create_reply'), # 댓글 등록
    path('<int:comment_id>/<int:post_id>/comment_recommend', views.comment_recommend, 
         name = 'comment_recommend'), # 댓글 추천
    
    path('<int:comment_id>/<int:post_id>/remove_comment', views.remove_comment, 
         name = 'remove_comment'), # 댓글 삭제 확인
    path('<int:comment_id>/<int:post_id>/remove_comment_check', views.remove_comment_check, 
         name = 'remove_comment_check'), # 댓글 삭제
    
    path('<int:comment_id>/<int:post_id>/re_comment', views.re_comment, 
         name = 're_comment'), # 댓글 수정 확인
    path('<int:comment_id>/<int:post_id>/re_comment_write', views.re_comment_write, 
         name = 're_comment_write'), # 댓글 수정
    path('<int:comment_id>/<int:post_id>/re_comment_write_ok', views.re_comment_write_ok, 
         name = 're_comment_write_ok'), # 댓글 수정 완료
]