# -*- coding: UTF-8 -*-
import hashlib
import urllib
from urllib import parse
import urllib.request
import base64
import time
import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.iai.v20200303 import iai_client, models
from PIL import Image
import cv2 as cv
import os

url_preffix = 'https://api.ai.qq.com/fcgi-bin/'


def setParams(array, key, value):
    array[key] = value


def genSignString(parser):
    uri_str = ''
    for key in sorted(parser.keys()):
        if key == 'app_key':
            continue
        uri_str += "%s=%s&" % (key, parse.quote(str(parser[key]), safe=''))
    sign_str = uri_str + 'app_key=' + parser['app_key']

    hash_md5 = hashlib.md5(sign_str.encode('utf-8'))
    return hash_md5.hexdigest().upper()


class AiPlat(object):
    def __init__(self, app_id, app_key):
        self.app_id = app_id
        self.app_key = app_key
        self.data = {}
        self.url_data = ''

    def invoke(self, params):
        self.url_data = urllib.parse.urlencode(params).encode("utf-8")
        req = urllib.request.Request(self.url, self.url_data)
        try:
            rsp = urllib.request.urlopen(req)
            str_rsp = rsp.read().decode('utf-8')
            dict_rsp = json.loads(str_rsp)
            return dict_rsp
        except Exception as e:
            print(e)
            return {'ret': -1}

    def face_detectface(self, image, mode):
        self.url = url_preffix + 'face/face_detectface'
        setParams(self.data, 'app_id', self.app_id)
        setParams(self.data, 'app_key', self.app_key)
        setParams(self.data, 'mode', mode)
        setParams(self.data, 'time_stamp', int(time.time()))
        setParams(self.data, 'nonce_str', int(time.time()))
        image_data = base64.b64encode(image)
        setParams(self.data, 'image', image_data.decode("utf-8"))
        sign_str = genSignString(self.data)
        setParams(self.data, 'sign', sign_str)
        return self.invoke(self.data)

    def newApiPost(image):
        try:
            # 实例化一个认证对象，入参需要传入腾讯云账户 SecretId 和 SecretKey，此处还需注意密钥对的保密
            # 代码泄露可能会导致 SecretId 和 SecretKey 泄露，并威胁账号下所有资源的安全性。以下代码示例仅供参考，建议采用更安全的方式来使用密钥，请参见：https://cloud.tencent.com/document/product/1278/85305
            # 密钥可前往官网控制台 https://console.cloud.tencent.com/cam/capi 进行获取
            cred = credential.Credential("AKIDlOqJckeMxMWS2QaZMxMXUDk26xc5EG4e", "OXSZVDiz3vOdh5Nhy7avGUXQ8jogKjyH")
            # 实例化一个http选项，可选的，没有特殊需求可以跳过
            httpProfile = HttpProfile()
            httpProfile.endpoint = "iai.tencentcloudapi.com"

            # 实例化一个client选项，可选的，没有特殊需求可以跳过
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            # 实例化要请求产品的client对象,clientProfile是可选的
            client = iai_client.IaiClient(cred, "", clientProfile)

            newImage = base64.b64encode(image).decode("utf-8")
            # 将png转换为jpg以兼容更2k分辨率

            # 实例化一个请求对象,每个接口都会对应一个request对象
            req = models.DetectFaceRequest()
            params = {
                "Image": newImage,
                "MaxFaceNum": 1,
                "NeedFaceAttributes": 1,
                "NeedQualityDetection": 1
            }
            req.headers = {"X-TC-Region": "ap-guangzhou"}
            req.from_json_string(json.dumps(params))

            # 返回的resp是一个DetectFaceResponse的实例，与请求对象对应
            resp = client.DetectFace(req)
            # 输出json格式的字符串回包
            print(resp.to_json_string())
            return resp
        except TencentCloudSDKException as err:
            print(err)
            return "error"


    def PNG_JPG(PngPath):
        img = cv.imread(PngPath, 0)
        w, h = img.shape[::-1]
        infile = PngPath
        outfile = os.path.splitext(infile)[0] + ".jpg"
        img = Image.open(infile)
        try:
            if len(img.split()) == 4:
                # prevent IOError: cannot write mode RGBA as BMP
                r, g, b, a = img.split()
                img = Image.merge("RGB", (r, g, b))
                img.convert('RGB').save(outfile, quality=100)
                os.remove(PngPath)
            else:
                img.convert('RGB').save(outfile, quality=100)
                os.remove(PngPath)
            return outfile
        except Exception as e:
            print("PNG转换JPG 错误", e)


if __name__ == '__main__':
    try:
        # yes_or_no()
        with open('../optimized.jpg', 'rb') as bin_data:
            image_data = bin_data.read()
        AiPlat.newApiPost(image_data)
    except KeyboardInterrupt:
        adb.run('kill-server')
        print('谢谢使用')
        exit(0)
