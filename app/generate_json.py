import os, sys, json, time, requests, shutil
import face_recognition as fr 
import numpy as np
from app import saved_pics_path, gen_json_path, download_json_path, faces_json_path, backup_json_path


def generate_total_json(json_path, json_name):
    output = []

    if os.path.exists(r'app/genprocess.log'):
        os.remove(r'app/genprocess.log')
    if os.path.exists(gen_json_path + json_name):
        shutil.copy(gen_json_path + json_name, backup_json_path + json_name + '.' + str(time.time()).replace('.','') + ".cp")

    if json_name == "updatesquads.json" and os.path.exists(gen_json_path + "updatesquads.json"):
        with open(gen_json_path + "updatesquads.json", 'rb') as f:
            prev_json = f.readline()
            prev_array = json.loads(prev_json.decode())
            output.extend(prev_array)

    with open(json_path, 'rb') as file:
        raw_json = file.readline()
        json_array = json.loads(raw_json.decode())

        for element in json_array:
            player_name = str(element['play_id']) + element['season'] + str(element['comp_id']) + str(element['club_id'])
                
        # if models.faces_info.query.filter_by(play_ifcoach=element['play_ifcoach'],
        #                                         play_id=element['play_id'],
        #                                         play_name=element['play_name'],
        #                                         club_id=element['club_id'],
        #                                         comp_id=element['comp_id'],
        #                                         season=element['season']).first() is None:

            output_element = element
            photo_url = output_element['photo_url']
            out_pic_path = r'app/static/database_imgs/' + player_name.replace('/','_') + '.jpg'

            with open(out_pic_path, 'wb') as f:
                photo_url = requests.get(photo_url)
                f.write(photo_url.content)

            face_mat = fr.face_encodings(fr.load_image_file(out_pic_path))[0].tolist()
            output_element['face_mat'] = face_mat
            output.append(output_element)

            # cur_info = models.faces_info(play_ifcoach=element['play_ifcoach'],
            #                                 play_id=element['play_id'],
            #                                 play_name=element['play_name'],
            #                                 club_id=element['club_id'],
            #                                 comp_id=element['comp_id'],
            #                                 season=element['season'],
            #                                 pic_path=out_pic_path)
            # db.session.add(cur_info)
            # db.session.commit()
            print(player_name + "已经写入json。")
            with open(r'app/genprocess.log', 'a', encoding='utf-8') as f:
                f.write(player_name + "已经写入json。\n")
        # else:
        #     print("数据库中已经存在" + player_name)
        #     with open(r'app/genprocess.log', 'a', encoding='utf-8') as f:
        #         f.write("数据库中已经存在" + player_name + "\n")

    with open(gen_json_path + json_name, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False)
        print("======json文件写入结束=======")
    
    if json_name == "squads.json":
        shutil.copy(gen_json_path + json_name, faces_json_path + json_name)
        if os.path.exists(gen_json_path + 'updatesquads.json'):
            os.remove(gen_json_path + 'updatesquads.json')
        print("======json文件拷贝结束======")
        
    with open(r'app/genprocess.log', 'a', encoding='utf-8') as f:
        f.write("==========json文件写入结束===========\n")


def get_json_from_oss(url):
    raw_json = requests.get(url).json()
    json_name = url.split('/')[-1]
    json_path = download_json_path + json_name

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(raw_json, f, ensure_ascii=False)
    
    generate_total_json(json_path, json_name)

def download_json(url):
    raw_json = requests.get(url).json()
    json_name = url.split('/')[-1]
    json_path = faces_json_path + json_name
    
    if os.path.exists(json_path):
        return "Fail"

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(raw_json, f, ensure_ascii=False)

    return json_path


def main():
    url = "http://picture.sodasoccer.com/squads_json/squads.json"
    get_json_from_oss(url)
 
    
# if __name__ == '__main__':
#     main()