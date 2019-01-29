# -*- coding: UTF-8 -*-
from app import app, saved_pics_path
from flask import Flask, render_template, request, flash, url_for, redirect, jsonify, make_response
from threading import Thread
from .face_transformer import swap_faces, NoFaces, TooManyFaces
from .face_detect import detect_group, detect_single
from .face_fusion import mix_pics, assemble_pics
from .find_faces import find_locs
from .generate_json import get_json_from_oss, download_json
import base64, os, dlib, cv2, sys, time, glob, shutil, json
import numpy as np


@app.route('/')
def index():
    '''
    测试连接
    '''
    return "Hello, this is the face_detection backend!"


@app.route('/api/single', methods=['GET', 'POST'])
def single():
    if request.method == 'POST':
        if 'upload_img' in request.files:
            upload_img = request.files['upload_img']
            upload_img_path = saved_pics_path + 'upload_imgs/upload' + str(time.time()).replace('.', '') + '.jpg'
            upload_img.save(upload_img_path)
        else:
            return format_data(msg='No pictures received!', data=[])

        selected_json = "squads.json"
        if 'selected_json' in request.values:
            selected_json = request.values['selected_json']
            if selected_json.strip() == '':
                selected_json = "squads.json"
        
        try:
            single_rec_msg = detect_single(upload_img_path, selected_json)
        except NoFaces as e:
            return format_data(msg="No faces detected!", data=[])
        else:
            return format_data(msg="Detect successful!", data={
                "sim_rate": single_rec_msg[0],
                "player_info": single_rec_msg[1]
            })
    else:
        return format_data(msg='No useful information in the url.', data=[])


@app.route('/api/group', methods=['GET', 'POST'])
def group():
    if request.method == 'POST':
        if 'upload_img' in request.files:
            upload_img = request.files['upload_img']
            upload_img_path = saved_pics_path + 'upload_imgs/upload' + str(time.time()).replace('.', '') + '.jpg'
            upload_img.save(upload_img_path)
        else:
            return format_data(msg='No pictures received!', data=[])

        selected_json = "squads.json"
        if 'selected_json' in request.values:
            selected_json = request.values['selected_json']
            if selected_json.strip() == '':
                selected_json = "squads.json"

        
        try:
            group_rec_msg = detect_group(upload_img_path, selected_json)
        except NoFaces as e:
            return format_data(msg="No faces detected!", data=[])
        else:
            return format_data(msg="Detect successful!", data={
                "generate_path": ' https://aiimg.sodasoccer.com.cn' + group_rec_msg[0],
                "players_info": group_rec_msg[1]
            })
    else:
        return format_data(msg='No useful information in the url.', data=[])


@app.route('/api/swap', methods=['GET', 'POST'])
def swap():
    if request.method == 'POST':
        if 'template_path' in request.values and request.values['template_path'].strip() != '':
            template_path = r'/oss/pics_repo/swap_templates/' + request.values['template_path']
        else:
            return format_data(msg='No templates have been chosen!', data=[])

        if 'upload_img' in request.files:
            upload_img = request.files['upload_img']
            upload_img_path = saved_pics_path + 'upload_imgs/upload' + str(time.time()).replace('.', '') + '.jpg'
            upload_img.save(upload_img_path)
        else:
            return format_data(msg='No pictures received!', data=[])

        try:
            generate = swap_faces(template_path, upload_img_path)
        except TooManyFaces as e:
            return format_data(msg="Too many faces detected!", data=[])
        except NoFaces as e:
            return format_data(msg="No faces detected!", data=[])
        else:
            return format_data(msg="Generate finished!", data={
                "generate_path": ' https://aiimg.sodasoccer.com.cn' + generate
            })
            
    else:
        return format_data(msg='No useful information in the url.', data=[])


@app.route('/api/fusion', methods=['GET', 'POST'])
def fusion():
    if request.method == 'POST':
        if ('upload_img' in request.files) and ('template_img' in request.files):
            upload_img = request.files['upload_img']
            upload_img_path = saved_pics_path + 'upload_imgs/upload' + str(time.time()).replace('.', '') + '.jpg'
            upload_img.save(upload_img_path)

            template_img = request.files['template_img']
            template_path = saved_pics_path + 'upload_imgs/upload' + str(time.time()).replace('.', '') + '.jpg'
            template_img.save(template_path)
        else:
            return format_data(msg='No pictures received!', data=[])

        try:
            generate = mix_pics(upload_img_path, template_path)
        except TooManyFaces as e:
            return format_data(msg="Too many faces detected!", data=[])
        except NoFaces as e:
            return format_data(msg="No faces detected!", data=[])
        else:
            return format_data(msg="Generate finished!", data={
                "generate_path": [' https://aiimg.sodasoccer.com.cn'+i for i in generate]
            })
            
    else:
        return format_data(msg='No useful information in the url.', data=[])


@app.route('/api/assemble', methods=['GET', 'POST'])
def assemble():
    if request.method == 'POST':
        if ('upload_img' in request.files) and ('template_img' in request.files):
            upload_img = request.files['upload_img']
            upload_img_path = saved_pics_path + 'upload_imgs/upload' + str(time.time()).replace('.', '') + '.jpg'
            upload_img.save(upload_img_path)

            template_img = request.files['template_img']
            template_path = saved_pics_path + 'upload_imgs/upload' + str(time.time()).replace('.', '') + '.jpg'
            template_img.save(template_path)
        else:
            return format_data(msg='No pictures received!', data=[])

        try:
            generate = assemble_pics(upload_img_path, template_path)
        except TooManyFaces as e:
            return format_data(msg="Too many faces detected!", data=[])
        except NoFaces as e:
            return format_data(msg="No faces detected!", data=[])
        else:
            return format_data(msg="Generate finished!", data={
                "generate_path": ' https://aiimg.sodasoccer.com.cn' + generate
            })
            
    else:
        return format_data(msg='No useful information in the url.', data=[])


@app.route('/api/manipulate', methods=['GET', 'POST'])
def manipulate():
    if request.method == 'POST':
        if 'selected_option' in request.values:
            json_url = ""
            if request.values['selected_option'] == "generate_json":
                json_url = "http://picture.sodasoccer.com/squads_json/squads.json"
            if request.values['selected_option'] == "renew_json":
                json_url = "http://picture.sodasoccer.com/squads_json/updatesquads.json"
            thr = Thread(target=get_json_from_oss, args=[json_url])
            thr.start()
            return "正在写入JSON文件。请点击<a href='https://ai.sodasoccer.com.cn/genprocess.log'>这里(https://ai.sodasoccer.com.cn/genprocess.log)</a>随时查看进度。"
        else:
            return render_template("manipulate.html")
    else:
        return render_template("manipulate.html")


@app.route('/api/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'new_json_url' in request.values:
            new_json_url = request.values['new_json_url']
            msg = download_json(new_json_url)
            if msg == "Fail":
                return format_data(msg="Upload fail", data={
                    "result":"目录下已经存在同名文件，上传失败。请到/home/face_rec/detect_api/app/static/json_files/faces_json下查看。"
                })
            else:
                return format_data(msg="Upload success", data={
                    "result":msg
                })
        else:
            return format_data(msg="未成功得到POST", data=[])


@app.route('/api/template', methods=['GET', 'POST'])
def template():
    if request.method == 'POST':
        if 'template' in request.files:
            template = request.files['template']
            template_path = saved_pics_path + 'swap_templates/template' + str(time.time()).replace('.', '') + '.jpg'
            template.save(template_path)
            find_locs(template_path)
            return "坐标生成成功，请到'/oss/pics_repo/swap_templates/'下根据对应txt文档将需要替代的人脸坐标放在txt文档的第一行。"
        else:
            return "模板上传失败。"
    else:
        return render_template("template.html")


@app.route('/favicon.ico')
def favicon():
    return "no favicon."


@app.route('/<path>')
def text(path):
    base_dir = os.path.dirname(__file__)
    if path.split('.')[-1] == 'json':
        base_dir = base_dir + '/static/json_files/gen_json/'
    print(os.path.join(base_dir, path))
    resp = make_response(open(os.path.join(base_dir, path)).read())
    resp.headers["Content-type"]="text/plan; charset=UTF-8"
    return resp


def format_data(msg, data):
    '''
    生成json格式文件
    '''
    return jsonify(
        {
            "detect_msg": msg,
            "detect_data": data
        }
    )