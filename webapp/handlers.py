#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import re, time, json, logging, hashlib, base64, asyncio
from webframe import get, post
from model import User, Comment, Blog, Category, next_id
from config import configs
from aiohttp import web
from apis import Page, APIValueError, APIResourceNotFoundError
import markdown2

COOKIE_NAME = 'blogcookie'
_COOKIE_KEY = configs.session.secret

_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')

def check_admin(request):
    if request.__user__ is None or not request.__user__.admin:
        raise APIPermissionError()

def get_page_index(page_str):
    p = 1
    try:
        p = int(page_str)
    except ValueError as e:
        pass
    if p < 1:
        p = 1
    return p

def text2html(text):
    lines = map(lambda s: '<p>%s</p>' % s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'), filter(lambda s: s.strip() != '', text.split('\n')))
    return ''.join(lines)

def user2cookie(user, max_age):
    '''
    Generate cookie str by user.
    '''
    # build cookie string by: id-expires-sha1
    expires = str(int(time.time() + max_age))
    s = '%s-%s-%s-%s' % (user.id, user.password, expires, _COOKIE_KEY)
    L = [user.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
    return '-'.join(L)

async def cookie2user(cookie_str):
    '''
    Parse cookie and load user if cookie is valid.
    '''
    if not cookie_str:
        return None
    try:
        L = cookie_str.split('-')
        if len(L) != 3:
            return None
        uid, expires, sha1 = L
        if int(expires) < time.time():
            return None
        user = await User.find(uid)
        if user is None:
            return None
        s = '%s-%s-%s-%s' % (uid, user.password, expires, _COOKIE_KEY)
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            logging.info('invalid sha1')
            return None
        user.password = '******'
        return user
    except Exception as e:
        logging.exception(e)
        return None

@get('/')
async def index(request, *, page='1'):
    user = request.__user__
    page_index = get_page_index(page)

    #去掉__about__页面
    num = await Blog.find_number('count(id)') - 1

    page = Page(num)
    if num == 0:
        blogs = []
    else:
        blogs = await Blog.find_all(where='name<>?', args=['__about__'], orderby='created_at desc', limit=(page.offset, page.limit))
    return {
        '__template__': 'blogs.html',
        'page': page,
        'blogs': blogs,
        'user': user,

    }

@get('/about')
async def about(request):
    user = request.__user__
    blog = await Blog.find_all(where='name=?', args=['__about__'])
    blog[0].html_content = markdown2.markdown(blog[0].content, extras=['code-friendly', 'fenced-code-blocks'])

    return {
        '__template__': 'about.html',
        'blog': blog[0], 
        'user': user,
    }

@get('/blog/{id}')
async def get_blog(id):
    blog = await Blog.find(id)
    blog.view_count = blog.view_count + 1
    await blog.update()
    comments = await Comment.find_all('blog_id=?', [id], orderby='created_at desc')
    for c in comments:
        c.html_content = text2html(c.content)
    blog.html_content = markdown2.markdown(blog.content)
    return {
        '__template__': 'blog.html',
        'blog': blog,
        'comments': comments
    }

@get('/register')
def register():
    return {
        '__template__': 'register.html'
    }

@get('/signin')
def signin():
    return {
        '__template__': 'signin.html'
    }

@get('/signout')
def signout(request):
    referer = request.headers.get('Referer')
    r = web.HTTPFound(referer or '/')
    r.set_cookie(COOKIE_NAME, '-deleted-', max_age=0, httponly=True)
    logging.info('user signed out.')
    return r

@get('/category/{id}')
async def get_category(id, request, *, page='1'):
    user = request.__user__
    page_index = get_page_index(page) 

    #cats = await Category.find_all(orderBy='created_at desc')
    category = await Category.find(id)

    num = await Blog.find_number('count(id)', 'cat_id=?', [id])
    p = Page(num, page_index)
    if num == 0:
        blogs = []
    else:
        blogs = await Blog.find_all(where='cat_id=?', args=[id], orderBy='created_at desc', limit=(p.offset, p.limit))
#        for blog in blogs:
#            blog.html_summary = markdown(blog.summary, extras=['code-friendly', 'fenced-code-blocks'])
    return {
        '__template__': 'blogs_by_category.html',
        'user': user,
        #'cats': cats,
        'page': p,
        'category': category,
        'blogs': blogs,
    }


@get('/manage/')
def manage():
    return 'redirect:/manage/comments'

@get('/manage/comments')
def manage_comments(*, page='1'):
    return {
        '__template__': 'manage_comments.html',
        'page_index': get_page_index(page)
    }

@get('/manage/blogs')
def manage_blogs(*, page='1'):
    return {
        '__template__': 'manage_blogs.html',
        'page_index': get_page_index(page)
    }

@get('/manage/blogs/create')
async def manage_create_blog():
    cats = await Category.find_all(orderby='created_at desc')
    return {
        '__template__': 'manage_blog_edit.html',
        'id': '',
        'cats': cats,
        'action': '/api/blogs'
    }

@get('/manage/blogs/edit')
async def manage_edit_blog(*, id):
    cats = await Category.find_all(orderby='created_at desc')
    return {
        '__template__': 'manage_blog_edit.html',
        'id': id,
        'cats': cats,
        'action': '/api/blogs/%s' % id
    }

@get('/manage/users')
def manage_users(*, page='1'):
    return {
        '__template__': 'manage_users.html',
        'page_index': get_page_index(page)
    }

#__TODO category
@get('/manage/categorys')
def manage_categorys(*, page='1'):
    return {
        '__template__': 'manage_categorys.html',
        'page_index': get_page_index(page),
    }

@get('/manage/categorys/create')
def manage_create_category():
    return {
        '__template__': 'manage_category_edit.html',
        'id': '',
        'action': '/api/categorys'
    }

@get('/manage/categorys/edit')
def manage_edit_category(*, id):
    return {
        '__template__': 'manage_category_edit.html',
        'id': id,
        'action': '/api/categorys/%s' % id
    }

@post('/api/authenticate')
async def authenticate(*, email, password):
    if not email:
        raise APIValueError('email', 'Invalid email.')
    if not password:
        raise APIValueError('password', 'Invalid password.')
    users = await User.find_all('email=?', [email])
    if len(users) == 0:
        raise APIValueError('email', 'Email not exist.')
    user = users[0]
    # check passwd:
    sha1 = hashlib.sha1()
    sha1.update(user.id.encode('utf-8'))
    sha1.update(b':')
    sha1.update(password.encode('utf-8'))
    if user.password != sha1.hexdigest():
        raise APIValueError('password', 'Invalid password.')
    # authenticate ok, set cookie:
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user.password = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r

@get('/api/comments')
async def api_comments(*, page='1'):
    page_index = get_page_index(page)
    num = await Comment.find_number('count(id)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, comments=())
    comments = await Comment.find_all(orderby='created_at desc', limit=(p.offset, p.limit))
    return dict(page=p, comments=comments)

@post('/api/blogs/{id}/comments')
async def api_create_comment(id, request, *, content):
    user = request.__user__
    if user is None:
        raise APIPermissionError('Please signin first.')
    if not content or not content.strip():
        raise APIValueError('content')
    blog = await Blog.find(id)
    if blog is None:
        raise APIResourceNotFoundError('Blog')
    comment = Comment(blog_id=blog.id, user_id=user.id, user_name=user.name, user_image=user.image, content=content.strip())
    await comment.save()
    return comment

@post('/api/comments/{id}/delete')
async def api_delete_comments(id, request):
    check_admin(request)
    c = await Comment.find(id)
    if c is None:
        raise APIResourceNotFoundError('Comment')
    await c.remove()
    return dict(id=id)

@get('/api/users')
async def api_get_users(*, page='1'):
    page_index = get_page_index(page)
    num = await User.find_number('count(id)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, users=())
    users = await User.find_all(orderby='created_at desc', limit=(p.offset, p.limit))
    for u in users:
        u.passwd = '******'
    return dict(page=p, users=users)

@post('/api/users')
async def api_register_user(*, email, name, password):
    if not name or not name.strip():
        raise APIValueError('name')
    if not email or not _RE_EMAIL.match(email):
        raise APIValueError('email')
    if not password or not _RE_SHA1.match(password):
        raise APIValueError('password')
    users = await User.find_all('email=?', [email])
    if len(users) > 0:
        raise APIError('register:failed', 'email', 'Email is already in use.')
    uid = next_id()
    sha1_passwd = '%s:%s' % (uid, password)
    user = User(id=uid, name=name.strip(), email=email, password=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(), image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email.encode('utf-8')).hexdigest())
    await user.save()
    # make session cookie:
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user.password = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r

@post('/api/user/{id}/delete')
async def api_delete_user(id, request):
    check_admin(request)
    user = await User.find(id)
    if user is None:
        raise APIResourceNotFoundError('User')
    await user.remove()
    return dict(id=id)

@get('/api/blogs')
async def api_blogs(*, page='1'):
    page_index = get_page_index(page)
    num = await Blog.find_number('count(id)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, blogs=())
    blogs = await Blog.find_all(brderby='created_at desc', limit=(p.offset, p.limit))
    return dict(page=p, blogs=blogs)

@get('/api/blogs/{id}')
async def api_get_blog(*, id):
    blog = await Blog.find(id)
    return blog

@post('/api/blogs')
async def api_create_blog(request, *, name, summary, content, cat_name):
    check_admin(request)
    if not name or not name.strip():
        raise APIValueError('name', 'name cannot be empty.')
    if not summary or not summary.strip():
        raise APIValueError('summary', 'summary cannot be empty.')
    if not content or not content.strip():
        raise APIValueError('content', 'content cannot be empty.')
    if not cat_name or not cat_name.strip():
        cat_id = None
    else:
        cats = await Category.find_all(where='name=?', args=[cat_name.strip()])
        cat_id = cats[0].id
 
    blog = Blog(user_id=request.__user__.id, user_name=request.__user__.name, user_image=request.__user__.image, name=name.strip(), summary=summary.strip(), content=content.strip(), cat_id=cat_id, cat_name=cat_name.strip())
    await blog.save()
    return blog

@post('/api/blogs/{id}')
async def api_update_blog(id, request, *, name, summary, content, cat_name):
    check_admin(request)
    blog = await Blog.find(id)
    if not name or not name.strip():
        raise APIValueError('name', 'name cannot be empty.')
    if not summary or not summary.strip():
        raise APIValueError('summary', 'summary cannot be empty.')
    if not content or not content.strip():
        raise APIValueError('content', 'content cannot be empty.')

    blog.name = name.strip()
    blog.summary = summary.strip()
    blog.content = content.strip()

    if not cat_name or not cat_name.strip():
        blog.cat_id = None
        blog.cat_name = None
    else:
        blog.cat_name = cat_name.strip()
        cats = await Category.find_all(where='name=?', args=[cat_name.strip()])
        blog.cat_id = cats[0].id
 
    await blog.update()
    return blog

@post('/api/blogs/{id}/delete')
async def api_delete_blog(request, *, id):
    check_admin(request)
    blog = await Blog.find(id)
    await blog.remove()
    return dict(id=id)

@get('/api/categorys')
async def api_categorys(*, page='1'):
    page_index = get_page_index(page)
    num = await Category.find_number('count(id)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, categorys=())
    categorys = await Category.find_all(brderby='created_at desc', limit=(p.offset, p.limit))
    return dict(page=p, categorys=categorys)

@get('/api/categorys/{id}')
async def api_get_category(*, id):
    category = await Category.find(id)
    return category 

@post('/api/categorys')
async def api_create_category(request, *, name):
    check_admin(request)
    if not name or not name.strip():
        raise APIValueError('name', 'name cannot be empty.')
    category = Category(name=name.strip())
    await category.save()
    return category 

@post('/api/categorys/{id}')
async def api_update_category(id, request, *, name):
    check_admin(request)
    category = await Category.find(id)
    if not name or not name.strip():
        raise APIValueError('name', 'name cannot be empty.')
    category.name = name.strip()
    await category.update()
    return category 


@post('/api/categorys/{id}/delete')
async def api_delete_category(request, *, id):
    check_admin(request)
    category = await Category.find(id)
    await category.remove()
    return dict(id=id)
