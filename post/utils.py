def substring(txt, length=10):
    return txt[:length] if len(txt) > length else txt
    
def get_user(request):
    from post.models import MyUser
    user = request.session.get('login_session')
    if(user is not None):
        return MyUser.objects.filter(userid=user).first()
    
    
def get_post_by_id(id):
    from post.models import Post
    return Post.objects.filter(num=id).first()