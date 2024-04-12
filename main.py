import sys

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout,
                             QHBoxLayout, QLineEdit, QPushButton, QLabel, QDialog, QMainWindow, QTableWidget,
                             QTableWidgetItem)
from PyQt5.QtGui import QPixmap, QIcon, QPainter
from gold_game import Gold_Game
import socket
import cv2
import numpy as np
import threading
import time


# 绘制排行榜
class LeaderboardWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.table = QTableWidget(10, 3)
        # 已有的人数
        self.count = 0
        self.data = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle("排行榜")
        self.setGeometry((screen_width - 600) // 2, (screen_height - 400) // 2, 600, 400)

        # 创建表格
        self.table.setHorizontalHeaderLabels(["Rank", "Name", "score"])

        # 从文件中读取数据并更新排行榜
        self.update_leaderboard_from_file("rank.txt")

        # 创建布局并添加控件
        layout = QVBoxLayout()
        layout.addWidget(self.table)

        # 创建中心 widget 并设置布局
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def update_leaderboard_from_file(self, filename):
        try:
            with open(filename, "r") as f:
                for line in f:
                    name, score = line.strip().split(" ")
                    self.data.append((name, score))
                self.update_leaderboard(self.data)
        except FileNotFoundError:
            print(f"Error: {filename} not found.")

    def update_leaderboard(self, data):
        self.table.setRowCount(len(data))
        self.count = len(data)
        for i, (name, score) in enumerate(data):
            self.table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.table.setItem(i, 1, QTableWidgetItem(name))
            self.table.setItem(i, 2, QTableWidgetItem(score))

    def add_player(self, name, score):
        # 检查是否已经存在该玩家
        exists = False
        for i, (player_name, player_score) in enumerate(self.data):
            if player_name == name:
                exists = True
                if score >= int(player_score):
                    self.data[i] = (player_name, str(score))
        if not exists:
            # 添加新玩家到排行榜
            self.data.append((name, str(score)))
            self.data.sort(key=lambda x: str(x[1]), reverse=True)
        self.update_leaderboard(self.data)

    def write_to_txt(self):
        try:
            with open("rank.txt", "w") as f:
                for name, score in self.data:
                    f.write(f"{name} {score}\n")
        except IOError:
            print(f"Error: Could not write")


# 用于过场动画的绘制
class Loading(QWidget):
    def __init__(self):
        super(Loading, self).__init__()

        # 载入动画的背景图
        self.m_bk = QPixmap("image/loading_back.png")

        # 设置窗口的大小
        self.setFixedSize(self.m_bk.size())

        # 去掉窗口的边框
        self.setWindowFlags(Qt.FramelessWindowHint)

        # 将图片的背景设为透明
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 进度条的图片
        self.loading = QPixmap("image/loading1.png")
        self.m_progress = self.loading

        # 设置定时器
        self.timer = QTimer(self)

        # 定时器每隔15ms发出信号,执行update
        self.timer.timeout.connect(self.update_progress)

        # 进度条的长度
        self.m_dist = 15

        # 排行榜
        self.ranking = LeaderboardWindow()
        self.score = None
        self.name = None
        self.diction = {"ywx": "于*秀", "wjb": "王*宝", "visitor": "访客"}

    def update_progress(self):

        # 更新进度条的长度
        self.m_progress = self.loading.copy(0, 0, self.m_dist, self.loading.height())

        # 重绘窗口
        self.update()

        # 判断进度条是不是到头了
        if self.m_dist >= self.loading.width():
            # 定时器停止
            self.timer.stop()

            # 定时器销毁
            self.timer.deleteLater()
            self.log_in_success()
        else:
            # 一次增长5个进度条
            self.m_dist += 5

    def paintEvent(self, event):
        painter = QPainter(self)

        # 进度条后画，原因在于要浮于斗地主图片上方
        painter.drawPixmap(self.rect(), self.m_bk)
        painter.drawPixmap(54, 130, self.m_progress.width(), self.m_progress.height(), self.m_progress)

    def log_in_success(self):
        # sys.exit()
        with open("name.txt", 'r') as f:
            self.name = f.readline()
            dialog = QDialog(self)
            dialog.setWindowTitle("登陆成功!")
            dialog.setGeometry((screen_width - 640) // 2, (screen_height - 400) // 2, 640, 400)
            # 创建对话框的布局并添加控件
            layout = QVBoxLayout()

            label = QLabel("hello~ " + self.diction[self.name])
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("font-family: Arial; font-size: 24px;")

            label_image = QLabel()
            face_image = QPixmap("received_img.jpg")
            face_image = face_image.scaled(640, 360)
            label_image.setPixmap(face_image)
            # label_image.setScaledContents(True)
            # 按钮
            close_button = QPushButton("确认")
            close_button.setStyleSheet(
                "background-color: #6495ED; color: white; font-size: 14px;")  # 设置按钮的背景颜色、文字颜色和字体大小
            close_button.clicked.connect(dialog.close)
            close_button.clicked.connect(self.start_game)

            layout.addWidget(label_image)
            layout.addWidget(label)
            layout.addWidget(close_button)
            dialog.setLayout(layout)
            dialog.exec_()
        f.close()

    def start_game(self):
        # 开始金币游戏
        self.hide()

        def writer():
            # new_client = socket.socket()
            # new_client.connect(("192.168.173.201", 5555))
            # while True:  # 开始游戏按下后调用---重新连接服务器
            #     data = new_client.recv(1024)
            #     try:
            #         if data.decode() == 'R' or data.decode() == 'L' or data.decode() == 'S':
            #             with open("move.txt", "a+") as f:
            #                 f.write(data.decode() + "\n")
            #                 f.flush()
            #     except FileNotFoundError:
            #         print("打开失败")
            #     if not reader_thread.is_alive():
            #         break
            pass

        def reader():
            gold_game = Gold_Game()
            self.score = gold_game.start()

        writer_thread = threading.Thread(target=writer)
        reader_thread = threading.Thread(target=reader)

        writer_thread.start()
        reader_thread.start()

        writer_thread.join()
        reader_thread.join()
        # 因为要产生新窗口了，所以这个loading窗口需要关闭
        # self.close()

        self.ranking.add_player(self.name, self.score)
        self.ranking.show()
        self.ranking.write_to_txt()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("嵌入式大作业")
        self.setGeometry((screen_width - 600) // 2, (screen_height - 600) // 2, 600, 600)

        # 创建所有部件
        # 文本输入框
        self.button3 = QPushButton()
        self.button3.setFixedSize(600, 600)
        # self.button3.setMinimumSize(200, 200)

        # 加载图片
        self.button3_pixmap = QPixmap("image/button.png")
        # 将缩放后的图片设置为按钮图标
        self.button3.setIcon(QIcon(self.button3_pixmap))
        self.button3.setIconSize(self.button3.size())

        # 创建过场动画
        self.load = Loading()

        self.button_connect()
        self.display_layout()

    def button_connect(self):
        # 注册按钮回调
        self.button3.clicked.connect(self.start_pygame)

    def display_layout(self):
        # 创建布局(主布局，所有部件都会放进这里)
        main_layout = QVBoxLayout()

        main_layout.addWidget(self.button3)
        # 设置主布局
        self.setLayout(main_layout)

    def start_pygame(self):
        self.hide()
        self.load.show()
        # 启动定时器（每15ms发一次信号）
        self.load.timer.start(15)
        # 连接远程的板子
        # client = socket.socket()
        # client.connect(("192.168.173.201", 5555))
        # while True:
        #     data = client.recv(1024)
        #     if data:
        #         # 通知服务器已收到标志数据，可以发送图像数据
        #         client.send(b"ok")
        #         flag = data.decode().split(",")
        #         total = int(flag[0])  # 图像字节流数据的总长度
        #         name = flag[1]  # 识别结果
        #
        #         f = open("name.txt", "w+")
        #         f.write(name)
        #         f.close()
        #
        #         cnt = 0  # 接收到的数据计数
        #         img_bytes = b""  # 存放接收到的数据
        #         while cnt < total:
        #             data = client.recv(25600)
        #             img_bytes += data
        #             cnt += len(data)
        #             print("receive:" + str(cnt) + "/" + flag[0])
        #         # 通知服务器图像接收完毕
        #         client.send(b"ok")
        #         # 解析接收到的字节流数据，并本地保存图片
        #         img = np.asarray(bytearray(img_bytes), dtype="uint8")
        #         img = cv2.imdecode(img, cv2.IMREAD_COLOR)
        #         cv2.imwrite("received_img.jpg", img)
        #         # cv2.imshow("img", img)
        #         cv2.waitKey(1)
        #         print("已断开！")
        #         break
        # client.close()  # 人脸识别后连接中断



if __name__ == "__main__":
    f = open("move.txt", "w")
    f.close()
    app = QApplication(sys.argv)
    # 获得屏幕的分辨率大小
    desk = QApplication.desktop()
    screen_width = desk.width()
    screen_height = desk.height()
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())

