import os
import math
import sqlite3
import argparse
import numpy as np
from rockx import RockX
import cv2
import socket


class FaceDB:

    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()
        if not self._is_face_table_exist():
            self.cursor.execute("create table FACE (NAME text, VERSION int, FEATURE blob, ALIGN_IMAGE blob)")

    def load_face(self):
        all_face = dict()
        c = self.cursor.execute("select * from FACE")
        for row in c:
            name = row[0]
            version = row[1]
            feature = np.frombuffer(row[2], dtype='float32')
            align_img = np.frombuffer(row[3], dtype='uint8')
            align_img = align_img.reshape((112, 112, 3))
            all_face[name] = {
                'feature': RockX.FaceFeature(version=version, len=feature.size, feature=feature),
                'image': align_img
            }
        return all_face

    def insert_face(self, name, feature, align_img):
        self.cursor.execute("INSERT INTO FACE (NAME, VERSION, FEATURE, ALIGN_IMAGE) VALUES (?, ?, ?, ?)",
                            (name, feature.version, feature.feature.tobytes(), align_img.tobytes()))
        self.conn.commit()

    def _get_tables(self):
        cursor = self.cursor
        cursor.execute("select name from sqlite_master where type='table' order by name")
        tables = cursor.fetchall()
        return tables

    def _is_face_table_exist(self):
        tables = self._get_tables()
        for table in tables:
            if 'FACE' in table:
                return True
        return False


def get_max_face(results):
    max_area = 0
    max_face = None
    for result in results:
        area = (result.box.bottom - result.box.top) * (result.box.right * result.box.left)
        if area > max_area:
            max_face = result
    return max_face


def get_face_feature(image_path):
    img = cv2.imread(image_path)
    img_h, img_w = img.shape[:2]
    ret, results = face_det_handle.rockx_face_detect(img, img_w, img_h, RockX.ROCKX_PIXEL_FORMAT_BGR888)
    if ret != RockX.ROCKX_RET_SUCCESS:
        return None, None
    max_face = get_max_face(results)
    if max_face is None:
        return None, None
    ret, align_img = face_landmark5_handle.rockx_face_align(img, img_w, img_h,
                                                            RockX.ROCKX_PIXEL_FORMAT_BGR888,
                                                            max_face.box, None)
    if ret != RockX.ROCKX_RET_SUCCESS:
        return None, None
    if align_img is not None:
        ret, face_feature = face_recog_handle.rockx_face_recognize(align_img)
        if ret == RockX.ROCKX_RET_SUCCESS:
            return face_feature, align_img
    return None, None


def get_all_image(image_path):
    img_files = dict()
    g = os.walk(image_path)

    for path, dir_list, file_list in g:
        for file_name in file_list:
            file_path = os.path.join(path, file_name)
            if not os.path.isdir(file_path):
                img_files[os.path.splitext(file_name)[0]] = file_path
    return img_files


def import_face(face_db, images_dir):
    image_files = get_all_image(images_dir)
    image_name_list = list(image_files.keys())
    for name, image_path in image_files.items():
        feature, align_img = get_face_feature(image_path)
        if feature is not None:
            face_db.insert_face(name, feature, align_img)
            print('[%d/%d] success import %s ' % (image_name_list.index(name) + 1, len(image_name_list), image_path))
        else:
            print('[%d/%d] fail import %s' % (image_name_list.index(name) + 1, len(image_name_list), image_path))


def search_face(face_library, cur_feature):
    min_similarity = 10.0
    target_name = None
    target_face = None
    for name, face in face_library.items():
        feature = face['feature']
        ret, similarity = face_recog_handle.rockx_face_similarity(cur_feature, feature)
        if similarity < min_similarity:
            target_name = name
            min_similarity = similarity
            target_face = face
    if min_similarity < 1.0:
        return target_name, min_similarity, target_face
    return None, -1, None


if __name__ == '__main__':
    sser = socket.socket()  # 创建socket对象
    sser.bind(('0.0.0.0', 5555))  # 绑定主机和端口号
    sser.listen(3)
    conn, addr = sser.accept()  # 等待客户端连接
    print(f"Connected to client:{addr}")

    # 参数解析
    parser = argparse.ArgumentParser(description="RockX Pose Demo")
    parser = argparse.ArgumentParser(description="RockX Face Recognition Demo")
    parser.add_argument('-c', '--camera', help="camera index", type=int, default=0)
    parser.add_argument('-b', '--db_file', help="face database path", required=True)
    parser.add_argument('-d', '--device', help="target device id", type=str)
    args = parser.parse_args()

    # 创建RockX身体关键点和人脸句柄
    pose_body_handle = RockX(RockX.ROCKX_MODULE_POSE_BODY, target_device=args.device)
    face_det_handle = RockX(RockX.ROCKX_MODULE_FACE_DETECTION, target_device=args.device)
    face_landmark5_handle = RockX(RockX.ROCKX_MODULE_FACE_LANDMARK_5, target_device=args.device)
    face_recog_handle = RockX(RockX.ROCKX_MODULE_FACE_RECOGNIZE, target_device=args.device)
    face_track_handle = RockX(RockX.ROCKX_MODULE_OBJECT_TRACK, target_device=args.device)

    face_db = FaceDB(args.db_file)

    # load face from database
    face_library = face_db.load_face()
    print("load %d face" % len(face_library))

    cap = cv2.VideoCapture(args.camera)
    cap.set(3, 1280)
    cap.set(4, 720)
    last_face_feature = None

    recog_right = 0  # 人脸识别成功变量
    while True:
        ret, frame = cap.read()
        in_img_h, in_img_w = frame.shape[:2]

        if recog_right == 0:
            ret, results = face_det_handle.rockx_face_detect(frame, in_img_w, in_img_h, RockX.ROCKX_PIXEL_FORMAT_BGR888)
            ret, results = face_track_handle.rockx_object_track(in_img_w, in_img_h, 3, results)
            for result in results:
                # face align
                ret, align_img = face_landmark5_handle.rockx_face_align(frame, in_img_w, in_img_h,
                                                                        RockX.ROCKX_PIXEL_FORMAT_BGR888,
                                                                        result.box, None)

                # get face feature
                if ret == RockX.ROCKX_RET_SUCCESS and align_img is not None:
                    ret, face_feature = face_recog_handle.rockx_face_recognize(align_img)

                # search face
                if ret == RockX.ROCKX_RET_SUCCESS and face_feature is not None:
                    target_name, diff, target_face = search_face(face_library, face_feature)
                    recog_right = 1
                    print('recognize success')
                    if target_name is None:
                        target_name = 'visitor'
                    print(f"hello!", target_name)

                    cv2.imwrite("send.jpg", frame)  # 保存图片到server端
                    # 压缩图像
                    img_encode = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 99])[1]
                    # 转换为字节流
                    bytedata = img_encode.tostring()
                    # 标志数据，包括待发送的字节流长度、识别结果等数据，用’，’隔开
                    flag_data = (str(len(bytedata))).encode() + ",".encode() + (str(target_name)).encode()
                    conn.send(flag_data)  # 发送标志数据
                    # 接收客户端的应答
                    data = conn.recv(1024)
                    if "ok" == data.decode():
                        # 客户端已经收到标志数据，开始发送图像字节流数据
                        conn.send(bytedata)
                    data = conn.recv(1024)
                    if "ok" == data.decode():
                        # 客户端已经接收图像
                        break

        if recog_right == 1:  # 人脸识别成功
            conn, addr = sser.accept()
            cap.set(3, 640)
            cap.set(4, 480)
            while True:
                # 按帧读取图像
                ret, frame = cap.read()
                in_img_h, in_img_w = frame.shape[:2]
                # 使用RockX进行身体关键点识别
                ret, results = pose_body_handle.rockx_pose_body(frame, in_img_w, in_img_h,
                                                                RockX.ROCKX_PIXEL_FORMAT_BGR888)
                # 在图像上绘制身体关键点
                for result in results:
                    i = 0
                    ang3 = ang4 = ang5 = ang6 = 0
                    Rsx = Rex = Rhx = Lsx = Lex = Lhx = 0
                    Rsy = Rey = Rhy = Lsy = Ley = Lhy = 0
                    for p in result.points:
                        cv2.circle(frame, (p.x, p.y), 3, (0, 255, 0), 3)
                    for pairs in RockX.ROCKX_POSE_BODY_KEYPOINTS_PAIRS:
                        i += 1
                        pt1 = result.points[pairs[0]]
                        pt2 = result.points[pairs[1]]
                        if pt1.x <= 0 or pt1.y <= 0 or pt2.x <= 0 or pt2.y <= 0:
                            continue
                        if i == 3:
                            Rsx = pt1.x
                            Rsy = pt1.y
                            Rex = pt2.x
                            Rey = pt2.y
                            ang3 = math.atan2(pt2.y - pt1.y, pt2.x - pt1.x)
                        if i == 4:
                            Rhx = pt2.x
                            Rhy = pt2.y
                            ang4 = math.atan2(pt2.y - pt1.y, pt2.x - pt1.x)
                        if i == 5:
                            Lsx = pt1.x
                            Lsy = pt1.y
                            Rex = pt2.x
                            Rey = pt2.y
                            ang5 = math.atan2(pt2.y - pt1.y, pt2.x - pt1.x)
                        if i == 6:
                            Lhx = pt2.x
                            Lhy = pt2.y
                            ang6 = math.atan2(pt2.y - pt1.y, pt2.x - pt1.x)
                        cv2.line(frame, (pt1.x, pt1.y), (pt2.x, pt2.y), (255, 0, 0), 2)

                    if abs(abs(ang3) - math.pi) <= math.pi / 5 and abs(
                            abs(ang5) - math.pi / 2) <= math.pi / 5:
                        print('Right')
                        conn.send("R".encode())
                    if abs(abs(ang3) - math.pi / 2) <= math.pi / 5 and abs(ang5) <= math.pi / 5:
                        print('Left')
                        conn.send("L".encode())
                    if abs(abs(ang3) - math.pi) <= math.pi / 5 and abs(ang5) <= math.pi / 5:
                        print('stand')
                        conn.send("S".encode())
                    if abs(abs(ang3) - math.pi / 2) <= math.pi / 5 and abs(
                            abs(ang5) - math.pi / 2) <= math.pi / 5:
                        print('stand')
                        conn.send("S".encode())

                # 显示结果图像
                cv2.imshow('RockX Pose - ' + str(args.device), frame)
                # 按下'q'键退出
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()

    pose_body_handle.release()
