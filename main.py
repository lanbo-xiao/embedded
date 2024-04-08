import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout,
                             QHBoxLayout, QLineEdit, QPushButton, QLabel,QDialog)
from PyQt5.QtGui import QPixmap, QIcon
from gold_game import Gold_Game


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("嵌入式大作业")
        self.setGeometry(100, 100, 1280, 720)

        # 创建所有部件
        # 文本输入框
        self.input_text = QLineEdit()
        self.input_text.setPlaceholderText("在这里输入游戏难度（数字）")
        # 创建按钮
        self.button1 = QPushButton("登录")
        self.button2 = QPushButton("开始游戏")
        self.button3 = QPushButton()
        self.button3.setFixedSize(600, 600)
        # self.button3.setMinimumSize(200, 200)

        # 加载图片
        self.button3_pixmap = QPixmap("image/button.png")
        # 将缩放后的图片设置为按钮图标
        self.button3.setIcon(QIcon(self.button3_pixmap))
        self.button3.setIconSize(self.button3.size())

        # 创建标签
        self.label = QLabel("This is a label")

        self.button_connect()
        self.display_layout()

    def button_connect(self):
        # 注册按钮回调
        self.button1.clicked.connect(self.face_detection)
        self.button2.clicked.connect(self.start_pygame)
        self.button3.clicked.connect(self.start_pygame)

    def display_layout(self):
        # 创建布局(主布局，所有部件都会放进这里)
        main_layout = QVBoxLayout()

        # 添加控件到布局
        main_layout.addWidget(self.input_text)

        # 按钮相关
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.button1)
        button_layout.addWidget(self.button2)
        main_layout.addLayout(button_layout)

        # 创建一个新的水平布局来放置 button3
        button3_layout = QHBoxLayout()
        button3_layout.addStretch()
        button3_layout.addWidget(self.button3)
        button3_layout.addStretch()
        main_layout.addLayout(button3_layout)

        main_layout.addWidget(self.label)
        # 设置主布局
        self.setLayout(main_layout)

    def face_detection(self):
        sys.exit()
        # with open("move.txt",'r') as f:
        #     name = f.readline()
        #     dialog = QDialog(self)
        #     dialog.setWindowTitle("登陆成功")
        #     dialog.setGeometry(400, 400, 200, 150)
        #     # 创建对话框的布局并添加控件
        #     layout = QVBoxLayout()
        #     label = QLabel("登陆成功，欢迎您,"+name)
        #     close_button = QPushButton("Close")
        #     close_button.clicked.connect(dialog.close)
        #     layout.addWidget(label)
        #     layout.addWidget(close_button)
        #     dialog.setLayout(layout)
        #     dialog.exec_()
        # f.close()

    def start_pygame(self):
        if self.input_text.text() in ['1', '2', '3', '4', '5']:
            gold_game = Gold_Game(int(self.input_text.text()))
        else:
            gold_game = Gold_Game()
        gold_game.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
