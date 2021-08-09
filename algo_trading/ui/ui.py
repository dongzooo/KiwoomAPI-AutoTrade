
from kiwoom import *
from PyQt5.QtWidgets import *

import sys

class UI_class():
    def __init__(self):
        print("UI_class 입니다.")

        self.app = QApplication(sys.argv) #UI에 사용할 변수 초기화
        #Kiwoom()

        self.kiwoom = Kiwoom()

        self.app.exec_()
UI_class()