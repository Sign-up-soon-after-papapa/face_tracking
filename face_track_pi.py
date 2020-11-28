import face_model_pi
import argparse
import cv2
import numpy as np


def feature_extract(face_box, frame):
    pass


def detect_faces(frame):
    face_boxes = []
    return face_boxes


def face_search(face_feature, feature_dict):
    pass


def mainloop():
    parser = argparse.ArgumentParser(description='face model test')
    # general
    parser.add_argument('--image-size', default='112,112', help='')
    parser.add_argument('--model', default='', help='path to load model.')
    parser.add_argument('--gpu', default=0, type=int, help='gpu id')
    args = parser.parse_args()

    vec = args.model.split(',')
    model_prefix = vec[0]
    model_epoch = int(vec[1])
    model = face_model_pi.FaceModel(args.gpu, model_prefix, model_epoch)

    # 读取视频流的每一帧并得到该帧的信息(时间，gps等)
    # url = 'rtsp://192.168.1.107:8080/11'
    # url = 'rtmp://live.hkstv.hk.lxdns.com/live/hks1'
    # url = 'rtsp://184.72.239.149/vod/mp4://BigBuckBunny_175k.mov'
    url = '/home/muyun99/MyGithub/face_tracking/hamilton_clip.mp4'

    video_capture = cv2.VideoCapture(url)

    # Todo:get frame infomation
    # while True:
    #     ret, frame = video_capture.read()
    #     cv2.imshow('frame', frame)
    #     cv2.waitKey(1)

    # feature_dict = {}
    frame_count = 0
    while (video_capture.isOpened()):
        if frame_count != 30:
            frame_count += 1
            continue
        else:
            frame_count = 0
        ret, frame = video_capture.read()

        # frame = cv2.imread('/home/muyun99/MyGithub/face_tracking/tom1.jpg')
        frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        result = model.detector.detect(frame, threshold=0.8)

        face_boxes = result[0]
        if len(face_boxes) != 0:
            for face_box in face_boxes:
                xmin, ymin, xmax, ymax, conf = face_box
                xmin = int(xmin)
                ymin = int(ymin)
                xmax = int(xmax)
                ymax = int(ymax)

                # face = frame[ymin:ymax, xmin:xmax]
                # face = cv2.resize(face, (112, 112))

                # face = model.get_input(face)
                # feature = model.get_feature(face)
                cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), color=(255, 255, 0))

        cv2.imshow('frame', frame)
        cv2.waitKey(1)
        # Todo:resize到112x112
        # face_boxes = model.detector.detect(frame, threshold=0.8)


    #     for face_box in face_boxes:
    #         # 计算每个人脸框的特征向量
    #         face_feature = feature_extract(face_box, frame)
    #
    #         # 搜索该人脸特征属于哪个人
    #         person_id = face_search(face_feature, feature_dict)
    #         if person_id == 0:
    #             # 新建一个person，写成一个response json
    #             response_json = {}
    #         else:
    #             # 组成一个response json
    #             response_json = {}
    #     # 将结果写入数据库
    #     # 并更新feature_dict


if __name__ == '__main__':
    mainloop()
