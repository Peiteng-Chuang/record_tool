# import sys
# import cv2
# import numpy as np
# import pyautogui
# import time
# from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QFileDialog
# from PySide6.QtCore import Qt, QRect, QTimer
# from PySide6.QtGui import QPainter, QColor, QPen, QIcon

# class ScreenRecorder(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("螢幕錄影工具")
#         self.setGeometry(100, 100, 300, 200)
#         self.setWindowFlags(Qt.Window)  # 設定為工具視窗，讓其他程式能正常操作

#         self.setWindowIcon(QIcon("pooh.png"))

#         # 介面佈局
#         layout = QVBoxLayout()
#         self.setLayout(layout)

#         self.label = QLabel("請選擇錄影範圍")
#         layout.addWidget(self.label)

#         self.select_button = QPushButton("選擇範圍")
#         self.select_button.clicked.connect(self.select_area)
#         layout.addWidget(self.select_button)

#         self.start_button = QPushButton("開始錄影")
#         self.start_button.setEnabled(False)
#         self.start_button.clicked.connect(self.start_recording)
#         layout.addWidget(self.start_button)

#         self.stop_button = QPushButton("停止錄影")
#         self.stop_button.setEnabled(False)
#         self.stop_button.clicked.connect(self.stop_recording)
#         layout.addWidget(self.stop_button)

#         # 在最下面加入製作者聲明
#         self.developer_label = QLabel("This tool is made by Payten")  # 請替換為你的名字
#         self.developer_label.setAlignment(Qt.AlignCenter)  # 置中顯示
#         self.developer_label.setStyleSheet("font-size: 10px; color: gray;")  # 設定字體大小和顏色
#         layout.addWidget(self.developer_label)

#         # 錄影相關變數
#         self.recording = False
#         self.recording_area = None
#         self.video_writer = None
#         self.timer = QTimer()
#         self.timer.timeout.connect(self.capture_frame)
#         self.overlay = None  # 用於顯示錄影範圍的透明標記框

#     def select_area(self):
#         """選擇錄影範圍"""
#         self.hide()  # 暫時隱藏 GUI，讓使用者更方便選取範圍
#         time.sleep(0.3)
#         self.recording_area = ScreenSelection.get_selected_area()
#         self.show()

#         if self.recording_area:
#             self.label.setText(f"選擇範圍: {self.recording_area}")
#             self.start_button.setEnabled(True)

#             # 顯示範圍標記框
#             if self.overlay:
#                 self.overlay.close()
#             self.overlay = RecordingOverlay(self.recording_area)
#             self.overlay.show()

#     def start_recording(self):
#         """開始錄影"""
#         if not self.recording_area:
#             return

#         file_path, _ = QFileDialog.getSaveFileName(self, "儲存影片", "", "MP4 Files (*.mp4)")
#         if not file_path:
#             return

#         self.recording = True
#         self.start_button.setEnabled(False)
#         self.stop_button.setEnabled(True)

#         x, y, w, h = self.recording_area
#         fps = 20.0
#         fourcc = cv2.VideoWriter_fourcc(*"mp4v")
#         self.video_writer = cv2.VideoWriter(file_path, fourcc, fps, (w, h))

#         self.timer.start(50)  # 每 50ms 擷取畫面

#     def stop_recording(self):
#         """停止錄影"""
#         self.recording = False
#         self.timer.stop()
#         if self.video_writer:
#             self.video_writer.release()
#             self.video_writer = None

#         self.label.setText("錄影完成！")
#         self.start_button.setEnabled(True)
#         self.stop_button.setEnabled(False)

#         # 關閉錄影範圍標記框
#         if self.overlay:
#             self.overlay.close()
#             self.overlay = None

#     def capture_frame(self):
#         """擷取畫面並寫入影片"""
#         if not self.recording or not self.video_writer:
#             return

#         x, y, w, h = self.recording_area
#         screenshot = pyautogui.screenshot(region=(x, y, w, h))
#         frame = np.array(screenshot)
#         frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
#         self.video_writer.write(frame)

# class ScreenSelection(QWidget):
#     """使用者拖曳選取螢幕範圍的視窗"""
#     selected_area = None

#     def __init__(self):
#         super().__init__()
#         self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
#         self.setWindowOpacity(0.4)
#         self.setGeometry(0, 0, *pyautogui.size())
#         self.start_pos = None
#         self.end_pos = None
#         self.setMouseTracking(True)
#         self.show()

#     def mousePressEvent(self, event):
#         self.start_pos = event.globalPosition().toPoint()
#         self.end_pos = self.start_pos

#     def mouseMoveEvent(self, event):
#         self.end_pos = event.globalPosition().toPoint()
#         self.update()

#     def mouseReleaseEvent(self, event):
#         self.end_pos = event.globalPosition().toPoint()
#         x1, y1 = self.start_pos.x(), self.start_pos.y()
#         x2, y2 = self.end_pos.x(), self.end_pos.y()
#         x, y = min(x1, x2), min(y1, y2)
#         w, h = abs(x2 - x1), abs(y2 - y1)

#         if w > 10 and h > 10:
#             ScreenSelection.selected_area = (x, y, w, h)

#         self.close()

#     def paintEvent(self, event):
#         if not self.start_pos or not self.end_pos:
#             return

#         painter = QPainter(self)
#         painter.setPen(QPen(QColor(255, 0, 0), 2, Qt.DashLine))
#         painter.drawRect(QRect(self.start_pos, self.end_pos))

#     @staticmethod
#     def get_selected_area():
#         """等待選取範圍"""
#         app = QApplication.instance()
#         if app is None:
#             app = QApplication(sys.argv)

#         selector = ScreenSelection()
#         while selector.isVisible():
#             app.processEvents()

#         return ScreenSelection.selected_area

# class RecordingOverlay(QWidget):
#     """顯示錄影範圍的透明標記框"""
#     def __init__(self, area):
#         super().__init__()
#         self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
#         self.setAttribute(Qt.WA_TranslucentBackground)
#         self.setGeometry(*area)
#         self.show()

#     def paintEvent(self, event):
#         """繪製紅色邊框"""
#         painter = QPainter(self)
#         painter.setPen(QPen(QColor(255, 0, 0), 3, Qt.SolidLine))
#         painter.drawRect(self.rect())

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = ScreenRecorder()
#     window.show()
#     sys.exit(app.exec())

import sys
import cv2
import numpy as np
import pyautogui
import time
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QFileDialog
from PySide6.QtCore import Qt, QRect, QTimer, QThread, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QIcon
import ctypes
import os

os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
os.environ["QT_SCALE_FACTOR"] = "1"

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception as e:
    print(f"DPI Awareness 設置失敗: {e}")

def resource_path(relative_path):
    """獲取打包後的資源路徑（適用於 PyInstaller）"""
    if hasattr(sys, '_MEIPASS'):  # PyInstaller 產生的執行檔會有 `_MEIPASS`
        return os.path.join(sys._MEIPASS, relative_path)
    return relative_path  # 開發環境時直接讀取


class CaptureThread(QThread):
    """專門用來擷取畫面的線程"""
    new_frame_signal = Signal(np.ndarray)

    def __init__(self, recording_area):
        super().__init__()
        self.recording_area = recording_area
        self.running = False

    def run(self):
        """開始擷取畫面"""
        x, y, w, h = self.recording_area
        while self.running:
            screenshot = pyautogui.screenshot(region=(x, y, w, h))
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            self.new_frame_signal.emit(frame)
            time.sleep(0.05)  # 每 50ms 擷取一次畫面，減少 CPU 使用率

    def stop(self):
        """停止畫面擷取線程"""
        self.running = False
        self.wait()  # 等待線程結束


class ScreenRecorder(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("螢幕錄影工具")
        self.setGeometry(100, 100, 300, 200)
        self.setWindowFlags(Qt.Window)

        icon_path = resource_path("pooh.png")
        self.setWindowIcon(QIcon(icon_path))

        # 介面佈局
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.label = QLabel("請選擇錄影範圍")
        layout.addWidget(self.label)

        self.select_button = QPushButton("選擇範圍")
        self.select_button.clicked.connect(self.select_area)
        layout.addWidget(self.select_button)

        self.start_button = QPushButton("開始錄影")
        self.start_button.setEnabled(False)
        self.start_button.clicked.connect(self.start_recording)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton("停止錄影")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_recording)
        layout.addWidget(self.stop_button)

        self.developer_label = QLabel("This tool is made by Payten")
        self.developer_label.setAlignment(Qt.AlignCenter)
        self.developer_label.setStyleSheet("font-size: 10px; color: gray;")
        layout.addWidget(self.developer_label)

        # 錄影相關變數
        self.recording = False
        self.recording_area = None
        self.video_writer = None
        self.overlay = None  # 用於顯示錄影範圍的透明標記框
        self.capture_thread = None  # 畫面擷取的線程

    def select_area(self):
        """選擇錄影範圍"""
        self.hide()  # 暫時隱藏 GUI，讓使用者更方便選取範圍
        time.sleep(0.3)
        self.recording_area = ScreenSelection.get_selected_area()
        self.show()

        if self.recording_area:
            self.label.setText(f"選擇範圍: {self.recording_area}")
            self.start_button.setEnabled(True)

            # 顯示範圍標記框
            if self.overlay:
                self.overlay.close()
            self.overlay = RecordingOverlay(self.recording_area)
            self.overlay.show()

    def start_recording(self):
        """開始錄影"""
        if not self.recording_area:
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "儲存影片", "", "MP4 Files (*.mp4)")
        if not file_path:
            return
        
        self.recording = True
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        #調用overlay
        self.overlay.start_recording()

        x, y, w, h = self.recording_area
        fps = 20.0
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.video_writer = cv2.VideoWriter(file_path, fourcc, fps, (w, h))

        # 啟動畫面擷取線程
        self.capture_thread = CaptureThread(self.recording_area)
        self.capture_thread.new_frame_signal.connect(self.capture_frame)
        self.capture_thread.running = True
        self.capture_thread.start()

    def stop_recording(self):
        """停止錄影"""
        self.recording = False
        if self.capture_thread:
            self.capture_thread.stop()
            self.capture_thread = None

        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None

        self.label.setText("錄影完成！")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

        #調用overlay
        self.overlay.stop_recording()

        # # 關閉錄影範圍標記框
        # if self.overlay:
        #     self.overlay.close()
        #     self.overlay = None

    def capture_frame(self, frame):
        """將擷取到的畫面寫入影片"""
        if not self.recording or not self.video_writer:
            return
        self.video_writer.write(frame)


class ScreenSelection(QWidget):
    """使用者拖曳選取螢幕範圍的視窗"""
    selected_area = None

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setWindowOpacity(0.4)
        self.setGeometry(0, 0, *pyautogui.size())
        self.start_pos = None
        self.end_pos = None
        self.setMouseTracking(True)
        self.show()

    def mousePressEvent(self, event):
        self.start_pos = event.globalPosition().toPoint()
        self.end_pos = self.start_pos

    def mouseMoveEvent(self, event):
        self.end_pos = event.globalPosition().toPoint()
        self.update()

    def mouseReleaseEvent(self, event):
        self.end_pos = event.globalPosition().toPoint()
        x1, y1 = self.start_pos.x(), self.start_pos.y()
        x2, y2 = self.end_pos.x(), self.end_pos.y()
        x, y = min(x1, x2), min(y1, y2)
        w, h = abs(x2 - x1), abs(y2 - y1)

        if w > 10 and h > 10:
            ScreenSelection.selected_area = (x, y, w, h)

        self.close()

    def paintEvent(self, event):
        if not self.start_pos or not self.end_pos:
            return

        painter = QPainter(self)
        painter.setPen(QPen(QColor(255, 0, 0), 2, Qt.DashLine))
        painter.drawRect(QRect(self.start_pos, self.end_pos))

    @staticmethod
    def get_selected_area():
        """等待選取範圍"""
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        selector = ScreenSelection()
        while selector.isVisible():
            app.processEvents()

        return ScreenSelection.selected_area


class RecordingOverlay(QWidget):
    """顯示錄影範圍的透明標記框"""
    def __init__(self, area):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 擴大邊框範圍，避免框線被錄進去
        padding = 5  # 增加 5 像素的邊界
        x, y, w, h = area
        self.setGeometry(x - padding, y - padding, w + 2 * padding, h + 2 * padding)
        
        self.is_recording = False  # 控制框線顏色
        self.show()

    def start_recording(self):
        """開始錄影時，將框線顏色改為綠色"""
        self.is_recording = True
        self.update()

    def stop_recording(self):
        """停止錄影時，將框線顏色恢復為紅色"""
        self.is_recording = False
        self.update()

    def paintEvent(self, event):
        """根據錄影狀態繪製不同顏色的方框"""
        painter = QPainter(self)
        color = QColor(0, 255, 0) if self.is_recording else QColor(255, 0, 0)  # 綠色 or 紅色
        painter.setPen(QPen(color, 3, Qt.SolidLine))
        painter.drawRect(self.rect())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScreenRecorder()
    window.show()
    sys.exit(app.exec())
