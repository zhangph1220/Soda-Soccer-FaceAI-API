# -*-coding:utf-8-*-
import cv2, dlib, time, sys
import numpy as np
from app import saved_pics_path
from face_fusion import NoFaces, TooManyFaces, average_face



PREDICTOR_PATH = "app/static/shape_predictor_68_face_landmarks.dat"
SCALE_FACTOR = 1 
FEATHER_AMOUNT = 11

FACE_POINTS = list(range(17, 68))
MOUTH_POINTS = list(range(48, 61))
RIGHT_BROW_POINTS = list(range(17, 22))
LEFT_BROW_POINTS = list(range(22, 27))
RIGHT_EYE_POINTS = list(range(36, 42))
LEFT_EYE_POINTS = list(range(42, 48))
NOSE_POINTS = list(range(27, 35))
JAW_POINTS = list(range(0, 17))

# ALIGN_POINTS = (LEFT_BROW_POINTS + RIGHT_EYE_POINTS + LEFT_EYE_POINTS +
#                                RIGHT_BROW_POINTS + NOSE_POINTS + MOUTH_POINTS)


# OVERLAY_POINTS = [
#     LEFT_EYE_POINTS + RIGHT_EYE_POINTS + LEFT_BROW_POINTS + RIGHT_BROW_POINTS,
#     NOSE_POINTS + MOUTH_POINTS,
# ]

ALIGN_POINTS = (RIGHT_EYE_POINTS + LEFT_EYE_POINTS + NOSE_POINTS + MOUTH_POINTS)

OVERLAY_POINTS = [
    LEFT_EYE_POINTS + RIGHT_EYE_POINTS,
    NOSE_POINTS + MOUTH_POINTS,
]

COLOUR_CORRECT_BLUR_FRAC = 0.6

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(PREDICTOR_PATH)


def annotate_landmarks(im, landmarks):
    im = im.copy()
    for idx, point in enumerate(landmarks):
        pos = (point[0, 0], point[0, 1])
        cv2.putText(im, str(idx), pos,
                    fontFace=cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,
                    fontScale=0.4,
                    color=(0, 0, 255))
        cv2.circle(im, pos, 3, color=(0, 255, 255))
    return im

def draw_convex_hull(im, points, color):
    points = cv2.convexHull(points)
    cv2.fillConvexPoly(im, points, color=color)

def get_face_mask(im, landmarks):
    im = np.zeros(im.shape[:2], dtype=np.float64)

    for group in OVERLAY_POINTS:
        draw_convex_hull(im,
                         landmarks[group],
                         color=1)

    im = np.array([im, im, im]).transpose((1, 2, 0))

    im = (cv2.GaussianBlur(im, (FEATHER_AMOUNT, FEATHER_AMOUNT), 0) > 0) * 1.0
    im = cv2.GaussianBlur(im, (FEATHER_AMOUNT, FEATHER_AMOUNT), 0)

    return im
    
def transformation_from_points(points1, points2):
    points1 = points1.astype(np.float64)
    points2 = points2.astype(np.float64)

    c1 = np.mean(points1, axis=0)
    c2 = np.mean(points2, axis=0)
    points1 -= c1
    points2 -= c2

    s1 = np.std(points1)
    s2 = np.std(points2)
    points1 /= s1
    points2 /= s2

    U, S, Vt = np.linalg.svd(points1.T * points2)
    R = (U * Vt).T

    return np.vstack([np.hstack(((s2 / s1) * R, c2.T - (s2 / s1) * R * c1.T)),
                     np.matrix([0., 0., 1.])])

def read_im_and_landmarks(pic):
    im = cv2.imread(pic, cv2.IMREAD_COLOR)
    im = cv2.resize(im, (im.shape[1] * SCALE_FACTOR,
                         im.shape[0] * SCALE_FACTOR))
    
    rects = detector(im, 1)
    
    if len(rects) == 0:
        raise NoFaces("no faces")

    target_rects = rects[0]
    if len(rects) > 1:
        pic_name = pic.split('/')[-1]
        if pic_name[:8] == 'template':
            with open(pic + '.txt', 'r') as f:
                target_rects = f.readline().strip()
            
            for i in rects:
                if str(i) == target_rects:
                    target_rects = i
                    break

    s = np.matrix([[p.x, p.y] for p in predictor(im, target_rects).parts()])
    return im, s

def warp_im(im, M, dshape):
    output_im = np.zeros(dshape, dtype=im.dtype)
    cv2.warpAffine(im,
                   M[:2],
                   (dshape[1], dshape[0]),
                   dst=output_im,
                   borderMode=cv2.BORDER_TRANSPARENT,
                   flags=cv2.WARP_INVERSE_MAP)
    return output_im

def correct_colours(im1, im2, landmarks1):
    blur_amount = COLOUR_CORRECT_BLUR_FRAC * np.linalg.norm(
                              np.mean(landmarks1[LEFT_EYE_POINTS], axis=0) -
                              np.mean(landmarks1[RIGHT_EYE_POINTS], axis=0))
    blur_amount = int(blur_amount)
    if blur_amount % 2 == 0:
        blur_amount += 1
    im1_blur = cv2.GaussianBlur(im1, (blur_amount, blur_amount), 0)
    im2_blur = cv2.GaussianBlur(im2, (blur_amount, blur_amount), 0)

    im2_blur += (128 * (im2_blur <= 1.0)).astype(im2_blur.dtype)

    return (im2.astype(np.float64) * im1_blur.astype(np.float64) /
                                                im2_blur.astype(np.float64))

# pic1 is the body image; pic2 is the head image
def transform_pics(pic1, pic2):
    '''
    交换人脸

    :return: 生成图片地址
    :param pic1: 模板图片 
    :param pic2: 用户上传图片
    '''
    im1, landmarks1 = read_im_and_landmarks(pic1)
    # if read_im_and_landmarks(pic2) == "too many faces" or read_im_and_landmarks(pic2) == "no faces":
    #     return read_im_and_landmarks(pic2)
    im2, landmarks2 = read_im_and_landmarks(pic2)

    M = transformation_from_points(landmarks1[ALIGN_POINTS], landmarks2[ALIGN_POINTS])

    mask = get_face_mask(im2, landmarks2)
    warped_mask = warp_im(mask, M, im1.shape)
    combined_mask = np.max([get_face_mask(im1, landmarks1), warped_mask], axis=0)

    warped_im2 = warp_im(im2, M, im1.shape)
    warped_corrected_im2 = correct_colours(im1, warped_im2, landmarks1)

    output_im = im1 * (1.0 - combined_mask) + warped_corrected_im2 * combined_mask
    file_path = saved_pics_path + 'fusion_swap/swap' + str(time.time()).replace('.', '') + '.jpg'
    
    cv2.imwrite(file_path, output_im)
    return file_path[4:]

def swap_faces(pic1, pic2):
    return transform_pics(pic1, r'/oss/' + average_face(pic1, pic2))

def main():
    swap_faces("./template0.jpg", "./1.jpg")

if __name__ == '__main__':
    main()