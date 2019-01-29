# Soda_faceAI_API帮助文档

[TOC]



## 程序目录结构

主程序目录`/home/face_rec/`

---

```
  ├─face_rec_env        // API运行所需要的虚拟环境
  │
  ├─repo                // 旧版本的API仓库（备份）
  │
  ├─start_env.sh        //  虚拟环境启动脚本
  │
  └─detect_api          //  API根目录
    │  config.py                //  flask配置文件
    │  create_db.py             //  数据库生成文件
    │  run.py                   //  flask项目启动文件
    │  start_api.ini            //  uwsgi启动脚本以及配置信息
    │  requirements.txt         //  依赖环境信息
    │
    ├─uwsgi              //  uwsgi相关文件
    │  uwsgi.log              //  日志文件，通过该文件查看uwsgi的日志 
    │  uwsgi.status           //  查看uwsgi的运行状态
    │  uwsgi.sock
    │  uwsgi.pid
    │
    └─app                   //  主程序目录
       │  6EMuPLTUx6.txt                //  微信小程序用
       │  face_detect.py                //  人脸识别模块
       │  face_fusion.py                //  人脸融合模块
       │  face_transformer.py           //  人脸替换模块
       │  find_faces.py                 //  生成模板坐标
       │  generate_json.py              //  生成人脸特征JSON文件模块
       │  genprocess.log                //  人脸特征JSON生成进度文件
       │  models.py                     //  数据库模型
       │  views.py                      //  后台生成模块
       │  __init__.py                   //  初始化配置文件
       │
       ├─static             //  存放整个API需要用到的数据文件
       │  │  shape_predictor_68_face_landmarks.dat              //  面部五官识别训练数据包
       │  │  youhei.ttf                 //  字体（用于图片标注）
       │  │
       │  ├─database_imgs               //  数据库图片备份
       │  ├─json_files                  //  人脸矩阵相关文件
       │  │  ├─backup_json                        //  JSON文件备份（每次更新JSON时备份）
       │  │  ├─download_json                      //  从数据库下载的原始JSON（没有人脸矩阵信息）
       │  │  │      squads.json
       │  │  │
       │  │  ├─faces_json                         //  人脸识别时需要用的JSON文件
       │  │  └─gen_json                           //  对download_json处理后生成的JSON
       └─templates                      //   H5页面
          │  manipulate.html
          │  upload.html
          │  template.html
```



图片保存目录`/oss/pics_repo/`

---

```
  ├─fusion_swap                //  生成的换脸以及融合的照片
  │
  ├─group_marks                //  群脸识别生成的标注图
  │
  ├─upload_imgs                //  用户上传的图片
  │
  └─swap_templates             //  换脸用的模板
```



## API运行依赖环境 以及 启动、关闭和状态监控方法

### 依赖环境

整个API采用nginx+uwsgi+flask搭建，主要语言为Python。

+ Python 3.5.1

  需安装依赖的库以及对应版本：（`pip3 install -r requirements.txt`）

  |Package|Version|
  |--|--|
  |Babel|2.6.0|
  |blinker|1.4|
  |certifi|2018.4.16|
  |chardet|3.0.4|
  |click|6.7|
  |coverage|4.5.1|
  |decorator|4.3.0|
  |defusedxml|0.5.0|
  |dlib|19.13.1|
  |face-recognition|1.2.2|
  |face-recognition-models|0.3.0|
  |Flask|0.12|
  |Flask-Babel|0.11.2|
  |Flask-Login|0.4.1|
  |Flask-Mail|0.9.1|
  |Flask-OpenID|1.2.5|
  |Flask-Script|2.0.5|
  |Flask-SQLAlchemy|2.3.2|
  |Flask-WhooshAlchemy|0.56|
  |Flask-WTF|0.14.2|
  |flipflop|1.0|
  |gevent|1.3.3|
  |greenlet|0.4.13|
  |guess-language|0.2|
  |idna|2.7|
  |itsdangerous|0.24|
  |Jinja2|2.10|
  |MarkupSafe|1.0|
  |numpy|1.14.3|
  |opencv-python|3.4.1.15|
  |pbr|4.0.3|
  |Pillow|5.1.0|
  |pip|10.0.1|
  |PyMySQL|0.8.1|
  |python3-openid|3.1.0|
  |pytz|2018.4|
  |requests|2.19.1|
  |setuptools|39.2.0|
  |six|1.11.0|
  |SQLAlchemy|1.2.8|
  |sqlalchemy-migrate|0.11.0|
  |sqlparse|0.2.4|
  |Tempita|0.5.2|
  |urllib3|1.23|
  |uWSGI|2.0.17|
  |Werkzeug|0.14.1|
  |wheel|0.31.1|
  |Whoosh|2.7.4|
  |WTForms|2.2|

+ dlib安装：https://blog.csdn.net/u010793915/article/details/53908243

+ uwsgi+flask配置：http://www.cnblogs.com/Ray-liang/p/4173923.html?utm_source=tuicool



### 启动、关闭和状态监控方法

#### 启动

+ `cd /home/face_rec/ `
+ `source start_env.sh`   启动虚拟环境并进入detect_api目录下；若命令行前显示`(face_rec_env)`表示已经进入虚拟环境
+ `uwsgi start_api.ini`   启动flask项目，可通过`ps -e`检测项目是否启动

#### 关闭

+ `killall -9 uwsgi`

#### 状态监控

+ `cd /home/face_rec/detect_api/uwsgi/`
+ `cat uwsgi.log`



## API 以及 JSON/模板更新模块

### 0 球员信息说明

标准格式：

```json
 {
    "club_id": 807, 
    "comp_id": 1, 
    "photo_url": "http://pro-picture.oss-cn-beijing.aliyuncs.com/squads_photo/1529491006228.png", 
    "play_id": 148256, 
    "play_ifcoach": 0, 
    "play_name": "A.\u5e2d\u5c14\u74e6", 
    "season": "2018"
}
```

参数说明

| 参数         | 说明               |
| ------------ | ------------------ |
| club_id      | 俱乐部id           |
| comp_id      | 联赛id             |
| photo_url    | 数据库上的图片地址 |
| play_id      | 球员id             |
| play_ifcoach | 是否是教练         |
| play_name    | 球员姓名           |
| season       | 赛季               |



### 1 单张人脸识别

#### 1.1 功能描述

上传一张人脸图片，返回10个数据库中与他最匹配的球员信息

#### 1.2 请求说明

> 请求url：`https://ai.sodasoccer.com.cn/api/single`

#### 1.3 请求参数

| 字段          | 字段类型 | 说明                                                         |
| ------------- | -------- | :----------------------------------------------------------- |
| upload_img    | file     | 用户上传的图片                                               |
| selected_json | string   | 选择从什么人脸库里识别图片（比如：世界杯球员库，可以去`/home/face_rec/detect_api/app/static/json_files/faces_json/`下查看需要使用的json文件名）；若该字段为空，则默认为squads.json |

#### 1.4 返回结果

+ 正确返回：

  ```json
  {
      "detect_data": {
          "player_info": [
              
          ],
          "sim_rate": [
              
          ]
      },
      "detect_msg": "Detect successful!"
  }
  ```

  注：

  + "player_info"（球员信息）与"sim_rate"（人脸相似度）均为10位数组，一一对应；
  + 返回的球员可能会存在同样的球员但对应着数据库中不同图片，需前端简单处理。

  例子：

  ```json
  {
    "detect_data": {
      "player_info": [
        { 
          "club_id": 807, 
          "comp_id": 1, 
          "photo_url": "http://pro-picture.oss-cn-beijing.aliyuncs.com/squads_photo/1529491006228.png", 
          "play_id": 148256, 
          "play_ifcoach": 0, 
          "play_name": "A.\u5e2d\u5c14\u74e6", 
          "season": "2018"
        }, 
        {
          "club_id": 787, 
          "comp_id": 1, 
          "photo_url": "http://pro-picture.oss-cn-beijing.aliyuncs.com/squads_photo/1529526712920.png", 
          "play_id": 227705, 
          "play_ifcoach": 0, 
          "play_name": "\u6208\u96f7\u8328\u5361", 
          "season": "2018"
        }, 
        {
          "club_id": 809, 
          "comp_id": 1, 
          "photo_url": "http://pro-picture.oss-cn-beijing.aliyuncs.com/squads_photo/1529526073580.png", 
          "play_id": 193428, 
          "play_ifcoach": 0, 
          "play_name": "\u5f17\u9c81\u52d2", 
          "season": "2018"
        }, 
        {
          "club_id": 901, 
          "comp_id": 1, 
          "photo_url": "http://pro-picture.oss-cn-beijing.aliyuncs.com/squads_photo/1529516722720.png", 
          "play_id": 202526, 
          "play_ifcoach": 0, 
          "play_name": "\u5361\u5c14\u6c83", 
          "season": "2018"
        }, 
        {
          "club_id": 795, 
          "comp_id": 1, 
          "photo_url": "http://pro-picture.oss-cn-beijing.aliyuncs.com/squads_photo/1529505691626.png", 
          "play_id": 235864, 
          "play_ifcoach": 0, 
          "play_name": "\u5229\u74e6\u79d1\u7ef4\u5947", 
          "season": "2018"
        }, 
        {
          "club_id": 827, 
          "comp_id": 1, 
          "photo_url": "http://pro-picture.oss-cn-beijing.aliyuncs.com/squads_photo/1529482979489.png", 
          "play_id": 118014, 
          "play_ifcoach": 0, 
          "play_name": "\u5362\u5361\u65af\u00b7\u6bd4\u5229\u4e9a", 
          "season": "2018"
        }, 
        {
          "club_id": 809, 
          "comp_id": 1, 
          "photo_url": "http://pro-picture.oss-cn-beijing.aliyuncs.com/squads_photo/1529525960449.png", 
          "play_id": 118439, 
          "play_ifcoach": 0, 
          "play_name": "\u4f50\u9ed8", 
          "season": "2018"
        }, 
        {
          "club_id": 901, 
          "comp_id": 1, 
          "photo_url": "http://pro-picture.oss-cn-beijing.aliyuncs.com/squads_photo/1529516625641.png", 
          "play_id": 180760, 
          "play_ifcoach": 0, 
          "play_name": "\u5965\u7ef4\u591a", 
          "season": "2018"
        }, 
        {
          "club_id": 827, 
          "comp_id": 1, 
          "photo_url": "http://pro-picture.oss-cn-beijing.aliyuncs.com/squads_photo/1529482892343.png", 
          "play_id": 154746, 
          "play_ifcoach": 0, 
          "play_name": "\u5b89\u8428\u5c14\u8fea", 
          "season": "2018"
        }, 
        {
          "club_id": 805, 
          "comp_id": 1, 
          "photo_url": "http://pro-picture.oss-cn-beijing.aliyuncs.com/squads_photo/1529516884019.png", 
          "play_id": 112761, 
          "play_ifcoach": 0, 
          "play_name": "\u6258\u897f\u5947", 
          "season": "2018"
        }
      ], 
      "sim_rate": [
        0.4997429099790206, 
        0.44090146610000913, 
        0.4251552226866653, 
        0.3918622878538365, 
        0.3873016613240515, 
        0.38281302681205875, 
        0.3784285206002016, 
        0.37523225552753825, 
        0.36799407413829655, 
        0.3640457161381774
      ]
    }, 
    "detect_msg": "Detect successful!"
  }
  ```

+ 错误返回：

  ```json
  // 未检测到人脸
  {
    "detect_data": [], 
    "detect_msg": "No faces detected!"
  }
  ```

  ```json
  // 未接受到图片
  {
    "detect_data": [], 
    "detect_msg": "No pictures received!"
  }
  ```

### 2 多人脸识别

#### 2.1 功能描述

上传一张图片，返回一个对图片上所有人脸进行标记的新的图片连接

#### 2.2 请求说明

> 请求url：`https://ai.sodasoccer.com.cn/api/group`

#### 2.3 请求参数

| 字段          | 字段类型 | 说明                                                         |
| ------------- | -------- | :----------------------------------------------------------- |
| upload_img    | file     | 用户上传的图片                                               |
| selected_json | string   | 选择从什么人脸库里识别图片（比如：世界杯球员库，可以去`/home/face_rec/detect_api/app/static/json_files/faces_json/`下查看需要使用的json文件名）；若该字段为空，则默认为squads.json |

#### 2.4 返回结果

+ 正确返回：

  ```json
  {
      "detect_data": {
          "player_info": [
              
          ],
          "generate_path": ""
      },
      "detect_msg": "Detect successful!"
  }
  ```

  注：

  + "player_info"（球员信息）包含图片中所有球员的信息。

  例子：

  ```json
  // 该例子图片中只有一个人的脸，故info只有一人
  {
    "detect_data": {
      "generate_path": "https://sodaai.oss-cn-beijing.aliyuncs.com/pics_repo/group_marks/group15297553941844738.jpg", 
      "players_info": [
        {
          "club_id": 788, 
          "comp_id": 1, 
          "photo_url": "http://pro-picture.oss-cn-beijing.aliyuncs.com/squads_photo/1529494014821.png", 
          "play_id": 261079, 
          "play_ifcoach": 0, 
          "play_name": "\u6208\u6d1b\u6e29", 
          "season": "2018"
        }
      ]
    }, 
    "detect_msg": "Detect successful!"
  }
  ```

+ 错误返回：

  ```json
  // 未检测到人脸
  {
    "detect_data": [], 
    "detect_msg": "No faces detected!"
  }
  ```
  ```json
  // 未接受到图片
  {
    "detect_data": [], 
    "detect_msg": "No pictures received!"
  }
  ```



### 3 人脸交换

#### 3.1 功能描述

上传一张图片，与模板图片进行人脸交换

#### 3.2 请求说明

> 请求url：`https://ai.sodasoccer.com.cn/api/swap`

#### 3.3 请求参数

| 字段          | 字段类型 | 说明                                                         |
| ------------- | -------- | :----------------------------------------------------------- |
| upload_img    | file     | 用户上传的图片                                               |
| template_path | string   | 选择的模板文件名，需要以template开头（比如：template111.jpg） |

#### 3.4 返回结果

- 正确返回：

  ```json
  {
      "detect_data": {
          "generate_path": ""
      },
      "detect_msg": "Generated finished!"
  }
  ```

  例子：

  ```json
  {
    "detect_data": {
      "generate_path": "https://sodaai.oss-cn-beijing.aliyuncs.com/pics_repo/fusion_swap/swap15297561199595344.jpg"
    }, 
    "detect_msg": "Generate finished!"
  }
  ```

- 错误返回：

  ```json
  // 未检测到人脸
  {
    "detect_data": [], 
    "detect_msg": "No faces detected!"
  }
  ```
  ```json
  // 用户上传的图片中有两张（含）以上的脸
  {
    "detect_data": [], 
    "detect_msg": "Too many faces detected!"
  }
  ```
  ```json
  // 为接收到模板信息
  {
    "detect_data": [], 
    "detect_msg": "No templates have been chosen!"
  }
  ```

  ```json
  // 为接收到图片
  {
    "detect_data": [], 
    "detect_msg": "No pictures received!"
  }
  ```

  

### 4 人脸融合（返回多张渐变图片）

#### 4.1 功能描述

上传一张图片，与模板图片进行人脸融合，并返回六张渐变的图片

#### 4.2 请求说明

> 请求url：`https://ai.sodasoccer.com.cn/api/fusion`

#### 4.3 请求参数

| 字段         | 字段类型 | 说明           |
| ------------ | -------- | :------------- |
| upload_img   | file     | 用户上传的图片 |
| template_img | file     | 模板图片       |

#### 4.4 返回结果

- 正确返回：

  ```json
  {
      "detect_data": {
          "generate_path": [
              
          ]
      },
      "detect_msg": "Generated finished!"
  }
  ```

  例子：

  ```json
  {
    "detect_data": {
      "generate_path": [
        "https://sodaai.oss-cn-beijing.aliyuncs.compics_repo/fusion_swap/fusion15297564413876266.jpg", 
        "https://sodaai.oss-cn-beijing.aliyuncs.compics_repo/fusion_swap/fusion15297564417775526.jpg", 
        "https://sodaai.oss-cn-beijing.aliyuncs.compics_repo/fusion_swap/fusion15297564422245197.jpg", 
        "https://sodaai.oss-cn-beijing.aliyuncs.compics_repo/fusion_swap/fusion1529756442819126.jpg", 
        "https://sodaai.oss-cn-beijing.aliyuncs.compics_repo/fusion_swap/fusion15297564433616674.jpg", 
        "https://sodaai.oss-cn-beijing.aliyuncs.compics_repo/fusion_swap/fusion1529756443919327.jpg"
      ]
    }, 
    "detect_msg": "Generate finished!"
  }
  ```

- 错误返回：

  ```json
  // 未检测到人脸
  {
    "detect_data": [], 
    "detect_msg": "No faces detected!"
  }
  ```

  ```json
  // 用户上传的图片中有两张（含）以上的脸
  {
    "detect_data": [], 
    "detect_msg": "Too many faces detected!"
  }
  ```
  ```json
  // 为接收到图片
  {
    "detect_data": [], 
    "detect_msg": "No pictures received!"
  }
  ```

  

### 5 人脸融合（返回单张渐变图片）

#### 5.1 功能描述

上传一张图片，与模板图片进行人脸融合，并返回单张渐变的图片，相当于把4生成的图片拼接在一起

#### 5.2 请求说明

> 请求url：`https://ai.sodasoccer.com.cn/api/assemble`

#### 5.3 请求参数

| 字段         | 字段类型 | 说明           |
| ------------ | -------- | :------------- |
| upload_img   | file     | 用户上传的图片 |
| template_img | file     | 模板图片       |

#### 5.4 返回结果

- 正确返回：

  ```json
  {
      "detect_data": {
          "generate_path": ""
      },
      "detect_msg": "Generated finished!"
  }
  ```

  例子：

  ```json
  {
    "detect_data": {
      "generate_path": "https://sodaai.oss-cn-beijing.aliyuncs.com/pics_repo/fusion_swap/assemble1529756782848294.jpg"
    }, 
    "detect_msg": "Generate finished!"
  }
  ```

- 错误返回：

  ```json
  // 未检测到人脸
  {
    "detect_data": [], 
    "detect_msg": "No faces detected!"
  }
  ```

  ```json
  // 用户上传的图片中有两张（含）以上的脸
  {
    "detect_data": [], 
    "detect_msg": "Too many faces detected!"
  }
  ```
  ```json
  // 为接收到图片
  {
    "detect_data": [], 
    "detect_msg": "No pictures received!"
  }
  ```

  

### 6 模板文件上传（交换人脸用）

+ 登陆`https://ai.sodasoccer.com.cn/api/template`上传模板图片；
+ 上传成功后，查看服务器`/oss/pics_repo/swap_templates`中上传的图片以及和该图片同名的txt文件
+ 根据txt文件里提供的坐标找到需要替换的人脸坐标，并将该坐标放到放到txt文件中的第一行。



### 7 球员信息JSON文件交换

#### 7.1 球员信息（待生成人脸矩阵的JSON文件）上传

##### 7.1.1 更新上传地址

> `https://ai.sodasoccer.com.cn/api/manipulate`

##### 7.1.2 说明 

_**生成人脸矩阵过程会极大占用CPU和内存，请尽量保证生成期间服务器不进行其他操作！**_

+ 完整生成JSON文件：
  + 服务器将会从`http://picture.sodasoccer.com/squads_json/squads.json `下载`squads.json`保存到`app/static/json_files/download_json`下
  + 在`app/static/json_files/backup_json/`下制作`app/static/json_files/gen_json/squads.json `的备份
  + 分析json文件内容并生成含有人脸矩阵的json文件，生成过程通过`https://ai.sodasoccer.com.cn/genprocess.log`实时查看
  + 生成结束后会保存并覆盖原有的`app/static/json_files/gen_json/squads.json `
  + 删除`app/static/json_files/gen_json/updatesquads.json `
+ 小部分更新JSON文件
  + 服务器将会从`http://picture.sodasoccer.com/squads_json/updatesquads.json `下载`updatesquads.json`保存到`app/static/json_files/download_json`下
  + 在`app/static/json_files/backup_json/`下制作`app/static/json_files/gen_json/updatesquads.json `的备份
  + 分析json文件内容并生成含有人脸矩阵的json文件，生成过程通过`https://ai.sodasoccer.com.cn/genprocess.log`实时查看
  + 生成结束后会保存*不会覆盖*原有的`app/static/json_files/gen_json/updatesquads.json `



#### 7.2 切割JSON

读取JSON文件地址：

> `https://ai.sodasoccer.com.cn/squads.json`
>
> `https://ai.sodasoccer.com.cn/updatesquads.json`



#### 7.3 切割好的JSON文件上传

##### 7.3.1功能说明

上传已经切割好的JSON文件（包含人脸矩阵）至服务器。请保留上传成功的JSON文件名，供前端进行人脸识别调用时使用。

##### 7.3.2 请求说明

> `https://ai.sodasoccer.com.cn/api/upload`

##### 7.3.3 请求参数

| 参数         | 类型|说明 |
| ------------ | ---- |----|
| new_json_url | string |切割好的json文件url（保证上传的文件是json格式，否则会导致500错误）|

##### 7.3.4 返回结果

+ 正确返回例子：

  ```json
  {
    "detect_data": {
      "result": "app/static/json_files/faces_json/updatesquads.json"
    }, 
    "detect_msg": "Upload success"
  }
  ```

+ 错误返回例子：

  ```json
  // 存在同名文件导致上传失败，请到/home/face_rec/detect_api/app/static/json_files/faces_json下查看。
  {
    "detect_data": {
      "result": "\u76ee\u5f55\u4e0b\u5df2\u7ecf\u5b58\u5728\u540c\u540d\u6587\u4ef6\uff0c\u4e0a\u4f20\u5931\u8d25\u3002\u8bf7\u5230/home/face_rec/detect_api/app/static/json_files/faces_json\u4e0b\u67e5\u770b\u3002"
    }, 
    "detect_msg": "Upload fail"
  }
  ```

  
