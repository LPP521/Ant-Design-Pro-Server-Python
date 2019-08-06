from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.views import View
from User import models

# Create your views here.
import json
import ast
import hashlib


# MD5加密
def md5(arg):
    md5_str = hashlib.md5()
    b_str = arg.encode(encoding='utf-8')
    md5_str.update(b_str)
    str_md5 = md5_str.hexdigest()
    return str_md5


class StudentsView(View):

    # 如果用户账号存在则登录，不存在则创建
    def post(self, request, *args, **kwargs):
        res = {}
        data = list(request.POST.keys())[0]
        json_data = json.loads(data)
        username = json_data.get('userName', '')
        password = json_data.get('password', '')
        if username and password:
            user_queryset = models.UserModel.objects.filter(username=username).first()
            if not user_queryset:
                data = {}
                data['username'] = username
                data['password'] = md5(password)
                data['token'] = md5(username)
                models.UserModel.objects.create(**data)
                res['status'] = 'ok'
                res['currentAuthority'] = 'user'
                res['message'] = u'注册成功'
                res['token'] = md5(username)
                return JsonResponse(res)
            else:
                if md5(password) == user_queryset.password:
                    res['status'] = 'ok'
                    res['currentAuthority'] = 'user'
                    res['message'] = u'登录成功'
                    res['token'] = user_queryset.user_token
                    return JsonResponse(res)
                else:
                    res['status'] = 'error'
                    res['currentAuthority'] = 'user'
                    res['message'] = u'登录失败'
                    res['token'] = ''
                    return JsonResponse(res)
        return JsonResponse(res)

    def put(self, request, *args, **kwargs):
        return HttpResponse('PUT')

    def delete(self, request, *args, **kwargs):
        return HttpResponse('DELETE')

# 临时登录接口
def user_login(request):
    result = {}
    dict_data = eval(str(request.body)).decode()
    ret = json.loads(dict_data)
    if request.method == "POST":
        username = ret['username']
        pwd = ret['password']
        user_modal = models.UserModel.objects.filter(username=username).first()
        print(user_modal)

        if md5(pwd) == user_modal.password:
            result['code'] = 200
            result['message'] = u'登录成功'
            result['token'] = user_modal.user_token
        else:
            result['code'] = 201
            result['message'] = u'登陆失败'
    return JsonResponse(result)


class RoutersData(View):

    def get(self, request, *args, **kwargs):
        return HttpResponse([])

    def post(self, request, *args, **kwargs):
        return HttpResponse([])


class UserInfo(View):
    # 获取用户信息
    def get(self, request, *args, **kwargs):
        token_arg = request.GET.get('token', 0)
        userInfo = models.UserModel.objects.filter(user_token=token_arg).first()
        data = {
            "user": userInfo.username,
            "name": userInfo.username,
            "avatar": 'https://www.wuyongcong.com/uploads/201903/avatar_15906d9cfe68cc32_small.jpeg',
            "userid": userInfo.id,
        }
        return JsonResponse(data)


# 获取用户列表
def user_date_list(reqeust):
    userobj = models.UserModel.objects.all()
    datalist = []
    for i in userobj:
        data = {}
        data['ID'] = i.id
        data['loginNum'] = i.username
        data['token'] = i.user_token
        data['createTime'] = i.register_time.strftime("%Y-%m-%d %H:%M:%S")
        datalist.append(data)
    result = {
        'code': 200,
        'message': u'请求数据成功',
        'data': datalist
    }
    return JsonResponse(result)


class UserdataView(View):

    # 修改用户登录账号
    def post(self, request):
        result = {}
        data = list(request.POST.keys())[0]
        json_data = json.loads(data)
        try:
            user_login_num = json_data['yuanShiLogin']  # 原始登录账号
            login_num = json_data['loginNum']
        except Exception as e:
            result['message'] = u'登陆凭证过期,退出重新登录!'  # Token过期
            result['code'] = 201
            return JsonResponse(result)
        filter_data = models.UserModel.objects.filter(username=user_login_num).update(username=login_num)
        if filter_data:
            result['message'] = u'修改成功'
            result['code'] = 200
            return JsonResponse(result)
        else:
            result['message'] = u'修改失败'
            result['code'] = 201
            return JsonResponse(result)


#  删除用户
def del_user_info(request):
    result = {}
    try:
        data = list(request.POST.keys())[0]
        json_data = json.loads(data)
        models.UserModel.objects.filter(id=json_data['userID']).delete()
        result['message'] = u'删除成功'
        result['code'] = 200
    except Exception as e:
        result['message'] = u'删除失败，错误原因: {0}'.format(e)
        result['code'] = 201
    return JsonResponse(result)


def add_user_info(request):
    result = {}
    data = list(request.POST.keys())[0]
    json_data = json.loads(data)
    filter_user = models.UserModel.objects.filter(username=json_data['LoginNum'])
    if filter_user:
        result['message'] = u'当前用户已存在'
        result['code'] = 201
    else:
        if json_data['LoginNum'] and json_data['loginPwd']:
            user_data = {'username': json_data['LoginNum'],
                         'password': md5(json_data['loginPwd']),
                         'user_token': md5(json_data['LoginNum'])}
            models.UserModel.objects.create(**user_data)
            result['message'] = u'新增成功'
            result['code'] = 200
        else:
            result['message'] = u'请确定是否输入登录账号或密码'
            result['code'] = 201
    return JsonResponse(result)


def add_aritive_data(request):
    result = {}
    data = list(request.POST.keys())[0]
    json_data = json.loads(data)
    try:
        aritice_data = {
            'title': json_data['title'],
            'aritice_user': json_data['user'],
            'aritice_gjz': json_data['gjz'],
            'img_url': json_data['imgPath'],
            'content': json_data['content']
        }
        models.AriticeModel.objects.create(**aritice_data)
        result['code'] = 200
        result['message'] = u'保存成功'
    except Exception as e:
        result['code'] = 201
        result['message'] = u'保存异常: {0}'.format(e)
    return JsonResponse(result)


def get_ariticle_list(request):
    result = {}
    aritlice_list = []
    data_list = models.AriticeModel.objects.all()
    try:
        for i in data_list:
            data_dict = {}
            data_dict['ID'] = i.id
            data_dict['imgPath'] = i.img_url
            data_dict['title'] = i.title
            data_dict['user'] = i.aritice_user
            data_dict['GJZ'] = i.aritice_gjz
            data_dict['Create_Time'] = i.create_time.strftime("%Y-%m-%d %H:%M:%S")
            aritlice_list.append(data_dict)
        result['message'] = u'获取成功'
        result['code'] = 200
        result['data'] = aritlice_list
    except Exception as e:
        result['message'] = u'获取错误: {0}'.format(e)
        result['code'] = 201
    return JsonResponse(result)


def add_mulu(request):
    result = {}
    data = list(request.POST.keys())[0]
    json_data = json.loads(data)
    if json_data['OneMulu']:
        try:
            models.DirectoryModel.objects.create(directtory_name=json_data['OneMulu'])
            result['code'] = 200
            result['message'] = u'添加成功'
        except Exception as e:
            result['code'] = 201
            result['message'] = u'添加异常: {0}'.format(e)
    else:
        result['code'] = 201
        result['message'] = u'一级目录参数获取错误，请联系工作人员!'
    return JsonResponse(result)


def get_one_mulu(request):
    result = {}
    data = []
    try:
        get_data = models.DirectoryModel.objects.all()
        for i in get_data:
            dict_data = {}
            dict_data['id'] = i.id
            dict_data['muluName'] = i.directtory_name
            data.append(dict_data)
        result['code'] = 200
        result['data'] = data
    except Exception as e:
        result['code'] = 201
        result['message'] = u'获取一级目录失败:{0}'.format(e)
    return JsonResponse(result)


# 获取二级目录，添加绑定一级目录关系
def add_two_mulu(request):
    result = {}
    data = list(request.POST.keys())[0]
    json_data = json.loads(data)
    try:
        models.Directory_Secondary.objects.create(secondary_name=json_data['TwoMulu'],
                                              directtore_id=models.DirectoryModel.objects.get(id=json_data['OneMulu']))
        result['code'] = 200
        result['message'] = u"添加成功"
    except Exception as e:
        result['code'] = 201
        result['message'] = u'添加异常: {0}'.format(e)
    return JsonResponse(result)


# 获取一， 二及目录给网页返回
def get_mulu(request):
    result = {}
    data = []
    one_modal = models.DirectoryModel.objects.all()
    if one_modal:
        for i in one_modal:
            one_dict = {}
            try:
                result['code'] = 200
                result['message'] = u"获取成功"
                result['data'] = data
                one_dict['Pid'] = i.id
                one_dict['name'] = i.directtory_name
                data.append(one_dict)
                two_modal = models.Directory_Secondary.objects.filter(directtore_id=models.DirectoryModel.objects.get(id=i.id))
                two_data = []
                for j in two_modal:
                    two_dict = {}
                    two_dict['id'] = j.id
                    two_dict['name'] = j.secondary_name
                    two_data.append(two_dict)
                    one_dict['data'] = two_data
            except Exception as e:
                result['code'] = 201
                result['message'] = u'获取错误: {0}'.format(e)
    return JsonResponse(result)


def get_one_mulu_data(request):
    result = {}
    dataList = []
    data = models.DirectoryModel.objects.all()
    try:
        for i in data:
            data = {}
            data['id'] = i.id
            data['name'] = i.directtory_name
            dataList.append(data)
        result['code'] = 200
        result['data'] = dataList
    except Exception as e:
        result['code'] = 201
        result['message'] = u'获取一级目录失败: {0}'.format(e)
    return JsonResponse(result)


def get_two_mulu_data(request):
    result = {}
    dataList = []
    data = list(request.POST.keys())[0]
    json_data = json.loads(data)
    # try:
    if json_data['MuLuPid']:
        data_modal = models.Directory_Secondary.objects.filter(directtore_id=models.DirectoryModel.objects.get(id=json_data['MuLuPid']))
        for i in data_modal:
            data_dict = {}
            data_dict['id'] = i.id
            data_dict['name'] = i.secondary_name
            dataList.append(data_dict)
        result['code'] = 200
        result['data'] = dataList
    # except Exception as e:
    #     print(e)
    #     result['data'] = []
    else:
        result['data'] = []
    return JsonResponse(result)


# 添加话术
def create_content(request):
    result = {}
    data = list(request.POST.keys())[0]
    json_data = json.loads(data)
    try:
        data = {
            'directory_secondary_id': models.Directory_Secondary.objects.get(id=json_data['TwoPID']),
            'directory_content': json_data['Context']
        }
        models.Content_Directory.objects.create(**data)
        result['code'] = 200
        result['message'] = u'内容添加成功'
    except Exception as e:
        result['code'] = 201
        result['message'] = u'内容添加失败: {0}'.format(e)
    return JsonResponse(result)


def get_context(request):
    result = {}
    dataList = []
    data = models.Content_Directory.objects.all()
    for i in data:
        try:
            dict_data = {}
            dict_data['ID'] = i.id
            dict_data['context'] = i.directory_content
            dict_data['secondary_name'] = i.directory_secondary_id.secondary_name
            dict_data['directory_name'] = i.directory_secondary_id.directtore_id.directtory_name
            dict_data['create_time'] = i.create_time.strftime("%Y-%m-%d %H:%M:%S")
            dataList.append(dict_data)
            result['code'] = 200
            result['message'] = u'获取成功'
            result['data'] = dataList
        except Exception as e:
            result['code'] = 201
            result['message'] = u'获取失败： {0}'.format(e)
    return JsonResponse(result)


def web_get_centext(request):
    result = {}
    dataList = []
    dict_data = eval(str(request.body)).decode()
    ret = json.loads(dict_data)
    Two_Mulu = models.Content_Directory.objects.filter(directory_secondary_id=models.Content_Directory.objects.get(id=ret['PID']))
    # Two_Mulu = models.Content_Directory.objects.filter(directory_secondary_id=2)
    try:
        for i in Two_Mulu:
            dict_data = {}
            dict_data['ID'] = i.id
            dict_data['context'] = i.directory_content
            dict_data['create_time'] = i.create_time.strftime("%Y-%m-%d %H:%M:%S")
            dataList.append(dict_data)
            result['code'] = 200
            result['data'] = dataList
    except Exception as e:
        result['code'] = 201
    return JsonResponse(result)


def context_update_del(request):
    result = {}
    data = list(request.POST.keys())[0]
    json_data = json.loads(data)
    print(json_data['ID'])
    if json_data['ID']:
        try:
            fiter_data = models.Content_Directory.objects.filter(id=json_data['ID'])
            fiter_data.update(directory_content=json_data['context'])
            result['code'] = 200
            result['message'] = u'修改成功'
        except Exception as e:
            result['code'] = 201
            result['message'] = u'修改失败: {0}'.format(e)
    return JsonResponse(result)


def web_get_context(request):
    result = {}
    data_list = []
    # data = list(request.POST.keys())[0]
    # json_data = json.loads(data)
    # print(json_data['PID'])
    context_id = request.POST.get('PID')
    try:
        data_queryset = models.Content_Directory.objects.filter(directory_secondary_id=context_id)
       # data_queryset = models.Content_Directory.objects.filter(directory_secondary_id=json_data['PID'])
        for i in data_queryset:
            data_dict = {}
            data_dict['ID'] = i.id
            data_dict['context'] = i.directory_content.replace('\n', '<br/>').replace('↵', '<br/>').replace(' ', '<br/>')
            data_list.append(data_dict)
        result['code'] = 200
        result['data'] = data_list
    except Exception as e:
        result['code'] = 201
        result['data'] = []
    return JsonResponse(result)











