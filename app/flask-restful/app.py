# -- coding: utf-8 --
from flask import Flask, render_template, request

from flask_restful import Resource, Api

import sys

from api_settng import imageinfo,licenseinfo,thumbnailhash,imagesall,imageshash,licesnsehash,deleteimg, settingparser,datacount,rangedata, updateimg



app = Flask(__name__)

api = Api(app)

# file 갯수 url
api.add_resource(datacount, '/info/datacount', methods=['GET'])

# licesne hash url
api.add_resource(licesnsehash, '/info/hash/license', methods=['GET'])

# image 세부정보 url
api.add_resource(imageinfo, '/info/original', methods=['GET'])

# license 세부정보 url
api.add_resource(licenseinfo, '/info/license', methods=['GET'])

# thumbnail hash url
api.add_resource(thumbnailhash, '/info/hash/thumbnail', methods=['GET'])

# 모든 데이터 url
api.add_resource(imagesall, '/api/images', methods=['GET'])

# image hash url
api.add_resource(imageshash, '/info/hash/original', methods=['GET'])

# crawler setting url
api.add_resource(settingparser, '/info/setting', methods=['GET'])

# image 범위검색 url
api.add_resource(rangedata, '/info/datarange', methods=['GET'])

# 이미지 삭제 url
api.add_resource(deleteimg, '/delete/image', methods=['DELETE'])

# 이미지 업데이트 url
api.add_resource(updateimg, '/update/imageinfo', methods=['PUT'])

@app.route('/')
def main():
    return render_template('main.html')

@app.route('/index', methods=['POST', 'GET'])
def index():
    _id = request.form['inputid']
    return render_template('index.html', id_ = _id)



if __name__ == '__main__':
    app.run(debug=True)
    # app.run()