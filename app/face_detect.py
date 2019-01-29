# -*-coding:utf-8-*-
import face_recognition as fr 
import numpy as np
import os, json, cv2, codecs, time
from .face_fusion import NoFaces, TooManyFaces
from app import faces_json_path, saved_pics_path
from PIL import Image, ImageDraw, ImageFont 



def detect_single(unknown_path, selected_json="squads.json"):
    faces_path = faces_json_path + selected_json
    unknown_img = fr.face_encodings(fr.load_image_file(unknown_path))
    if len(unknown_img) == 0:
        raise NoFaces("no faces")
    unknown_encoding = unknown_img[0]
   
    with open(faces_path, 'rb') as json_file:
        play_info = []
        rates = []

        raw_json = json_file.readline()
        infos = json.loads(raw_json.decode())
        for info in infos:
            rates.extend(similarity_rate([info.pop('face_mat')], unknown_encoding))
            play_info.append(info)

        tops = find_tops(rates, 10)
        top_sim_list = []
        top_info_list = []

        for i in tops:
            top_sim_list.append(rates[i])
            top_info_list.append(play_info[i])
        
        data_list = [(s_rate, p_info) for s_rate, p_info in zip(top_sim_list, top_info_list)]
        data_list.sort(reverse=True)
        top_sim_list = [s_rate for s_rate, p_info in data_list]
        top_info_list = [p_info for s_rate, p_info in data_list]
        # top_name_list = []
        # for i in top_info_list:
        #     top_name_list.append(i['play_name'])
        # max_rate = 0
        # max_idx = 0

        # for pic_id, sim_rate, name in zip(tops, top_sim_list, top_name_list):
        #     if sim_rate == 1.0:
        #         max_idx = pic_id
        #         max_rate = sim_rate
        #         break
        #     else:
        #         k = top_name_list.count(name)
        #         if k > 4:
        #             max_idx = pic_id
        #             max_rate = sim_rate
        #             break
        #         sim_rate = sim_rate * ((10 + k) / 10)
        #         if max_rate > sim_rate:
        #             continue
        #         else:
        #             max_rate = sim_rate
        #             max_idx = pic_id

        msg_list = []
        # msg_list.append(max_rate)
        # msg_list.append(play_info[max_idx])
        msg_list.append(top_sim_list)
        msg_list.append(top_info_list)
        return msg_list


def detect_group(unknown_path, selected_json="squads.json"):
    faces_path = faces_json_path + selected_json
    unknown_img = fr.face_encodings(fr.load_image_file(unknown_path))
    if len(unknown_img) == 0:
        raise NoFaces("no faces")
    
    face_locations = fr.face_locations(fr.load_image_file(unknown_path))
    sim_list = []
    info_list = []

    for player in unknown_img:
        with open(faces_path, 'rb') as json_file:
            play_info = []
            rates = []
           
            raw_json = json_file.readline()
            infos = json.loads(raw_json.decode())
            for info in infos:
                rates.extend(similarity_rate([info.pop('face_mat')], player))
                play_info.append(info)
           
            tops = find_tops(rates, 1)
           
            for i in tops:
                sim_list.append(rates[i])
                info_list.append(play_info[i])

    name_list = []
    for i in info_list:
        name_list.append(i['play_name'])

    image = cv2.imread(unknown_path)
    image_PIL = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    font = ImageFont.truetype('app/static/youhei.ttf', 20)
    draw = ImageDraw.Draw(image_PIL)
    for (top, right, bottom, left), name in zip(face_locations, name_list):
        draw.rectangle([(left, top), (right, bottom)], outline=(255, 0, 0))
        draw.rectangle([(left, bottom - 15), (right, bottom)], fill=(255, 0, 0), outline=(255, 0, 0))
        draw.text((left, bottom - 14), name, font=font, fill=(0, 255, 0))

    image = cv2.cvtColor(np.asarray(image_PIL), cv2.COLOR_RGB2BGR)
    new_file_name = saved_pics_path + 'group_marks/group' + str(time.time()).replace('.', '') + '.jpg'
    cv2.imwrite(new_file_name, image)
    msg_list = [new_file_name[4:], info_list]
    return msg_list


def find_tops(nums, amount):
    '''
    查找一个数组中最大的几个元素

    :return: 返回一个下标的列表
    :param nums: 待查询的数组 
    :param amount: 查找数组中最大的amount个数 
    '''
    # return the indexes
    a = np.array(nums)  
    return np.argpartition(a,-amount)[-amount:].tolist() 

def similarity_rate(known_face_encodings, face_encoding_to_check):
    '''
    人脸相似度判断

    :return: 返回一个相似度的数组
    '''
    return list(1 - fr.face_distance(known_face_encodings, face_encoding_to_check))
