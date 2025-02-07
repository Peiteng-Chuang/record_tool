import os
import sys
import cv2
import mss
import time
import ctypes
import win32api
import numpy as np
from PySide6.QtGui import QPainter, QColor, QPen, QIcon
from PySide6.QtCore import Qt, QRect, QThread, Signal
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QFileDialog, QComboBox

os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
os.environ["QT_SCALE_FACTOR"] = "1"

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception as e:
    print(f"DPI Awareness 設置失敗: {e}")

import sys
import os
from PySide6.QtGui import QIcon

def resource_path(relative_path):
    """ 取得正確的資源路徑 (打包後適用) """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return relative_path


class CaptureThread(QThread):
    """專門用來擷取畫面的線程"""
    new_frame_signal = Signal(np.ndarray)

    def __init__(self, recording_area, dpi_scaling, selected_screen_name):
        super().__init__()
        self.recording_area = recording_area
        self.dpi_scaling = dpi_scaling
        self.selected_screen_name = selected_screen_name  # 新增變數存儲螢幕名稱
        self.running = False

    def run(self):
        """開始擷取畫面"""
        x, y, w, h = self.recording_area
        print(f"輸入為 x, y, w, h = {x}, {y}, {w}, {h}")
        # 根據 DPI 進行縮放
        scaling = self.dpi_scaling[self.selected_screen_name]  # 取得所選螢幕的 DPI 縮放比例
        # print(f"錄影開始，設置{self.selected_screen_name}的dpi為{scaling}")
        
        # top_left = self.screen_geometry.topLeft()

        # x = int((x - top_left.x()) * scaling)
        # y = int((y - top_left.y()) * scaling)
        # w=int(w*scaling)
        # h=int(h*scaling)

        with mss.mss() as sct:
            monitor = {"top": y, "left": x, "width": w, "height": h}
            print(f"實際錄製為 x, y, w, h = {x}, {y}, {w}, {h}")
            while self.running:
                screenshot = sct.grab(monitor)
                frame = np.array(screenshot)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                self.new_frame_signal.emit(frame)
                time.sleep(0.05)

    def stop(self):
        """停止畫面擷取線程"""
        self.running = False
        self.wait()  # 等待線程結束



class ScreenRecorder(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("螢幕錄影工具")
        self.setGeometry(100, 100, 300, 250)
        self.setWindowFlags(Qt.Window)

        #外接資源路徑
        icon_path = resource_path("pooh.png")
        self.setWindowIcon(QIcon(icon_path))

        # 取得所有螢幕資訊
        self.screens = QApplication.screens()
        #================================================================
        #設置dpi抓取專用參數
        
        self.shcore = ctypes.windll.shcore
        self.monitors = win32api.EnumDisplayMonitors()
        #================================================================
        self.screen_list = {screen.name(): screen.geometry() for screen in self.screens}
        self.dpi_scaling = self.get_screen_dpi_scaling()  # 取得各螢幕的顯示比例

        # 介面佈局
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.screen_selector = QComboBox()
        self.screen_selector.addItems(self.screen_list.keys())
        self.screen_selector.currentIndexChanged.connect(self.update_screen_selection)
        layout.addWidget(self.screen_selector)

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

        self.recording = False
        self.recording_area = None
        self.video_writer = None
        self.overlay = None
        self.capture_thread = None
        self.selected_screen_name = list(self.screen_list.keys())[0]
        self.selected_screen_geometry = self.screen_list[self.selected_screen_name]
        
    def get_screen_dpi_scaling(self):
        """取得每個螢幕的 DPI 顯示比例"""
        base_dpi = 96.0  # Windows 100% DPI 的標準值
        #================================================================
        dpiX = ctypes.c_uint()
        dpiY = ctypes.c_uint()
        dpi_list =[]
        for i, monitor in enumerate(self.monitors):
            self.shcore.GetDpiForMonitor(
                monitor[0].handle,
                0,
                ctypes.byref(dpiX),
                ctypes.byref(dpiY)
            )
            dpi_list.append(dpiX.value)
            print(f"{dpiX.value} get")

        screen_dpi = {}
        # 倒轉 dpi_list 以匹配 self.screens 的順序
        dpi_list.reverse()

        for i, screen in enumerate(self.screens):
            # 使用 dpi_list 中的對應值替換 screen.logicalDotsPerInch()
            dpi = dpi_list[i] if i < len(dpi_list) else base_dpi  # 預防超出範圍，使用預設 DPI
            screen_dpi[screen.name()] = dpi / base_dpi  # 計算縮放比例

        #================================================================
        # screen_dpi = {
        #     screen.name(): screen.logicalDotsPerInch() / base_dpi
        #     for screen in self.screens
        # }
        return screen_dpi


    def update_screen_selection(self):
        """更新選擇的螢幕"""
        self.selected_screen_name = self.screen_selector.currentText()
        self.selected_screen_geometry = self.screen_list[self.selected_screen_name]
        print(f"{self.selected_screen_name} have been selected , DPI = {self.dpi_scaling[self.selected_screen_name]}")


    def select_area(self):
        """選擇錄影範圍"""
        self.hide()
        time.sleep(0.3)
        self.recording_area = ScreenSelection.get_selected_area(self.selected_screen_geometry, self.dpi_scaling[self.selected_screen_name])
        # print(f"現在是{self.selected_screen_name}, DPI = {self.dpi_scaling[self.selected_screen_name]}")
        self.show()

        if self.recording_area:
            self.label.setText(f"選擇範圍: {self.recording_area}")
            self.start_button.setEnabled(True)

            if self.overlay:
                self.overlay.close()
            self.overlay = RecordingOverlay(self.recording_area, self.dpi_scaling[self.selected_screen_name],self.selected_screen_geometry)
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

        self.overlay.start_recording()

        x, y, w, h = self.recording_area

        fps = 24.0
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.video_writer = cv2.VideoWriter(file_path, fourcc, fps, (w, h))

        

        print(f"start recording dpi={self.dpi_scaling[self.selected_screen_name]}")
        print(f"Recording at: {x}, {y}, {w}, {h} (Original: {self.recording_area})")

        self.capture_thread = CaptureThread(self.recording_area, self.dpi_scaling, self.selected_screen_name)
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

        self.overlay.stop_recording()

        if self.overlay:
            self.overlay.close()
            self.overlay = None

    def capture_frame(self, frame):
        """將擷取到的畫面寫入影片"""
        if not self.recording or not self.video_writer:
            return
        self.video_writer.write(frame)


class ScreenSelection(QWidget):
    def __init__(self, screen_geometry, dpi_scaling):
        super().__init__()
        self.screen_geometry = screen_geometry
        self.dpi_scaling = dpi_scaling
        self.setGeometry(screen_geometry)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setWindowOpacity(0.4)
        self.start_pos = None
        self.end_pos = None
        self.selected_area = None
        self.show()

    def mousePressEvent(self, event):
        self.start_pos = event.globalPosition().toPoint() - self.screen_geometry.topLeft()
        self.end_pos = self.start_pos

    def mouseMoveEvent(self, event):
        self.end_pos = event.globalPosition().toPoint() - self.screen_geometry.topLeft()
        self.update()

    def mouseReleaseEvent(self, event):
        """修正座標轉換，使其相對於全域座標系"""
        print(f"self.screen_geometry.topLeft()={self.screen_geometry.topLeft()}")

        global_start = self.mapToGlobal(self.start_pos)
        global_end = event.globalPosition().toPoint()

        x1, y1 = global_start.x(), global_start.y()
        x2, y2 = global_end.x(), global_end.y()

        x, y = min(x1, x2), min(y1, y2)
        w, h = abs(x2 - x1), abs(y2 - y1)

        # 根據 DPI 縮放
        scaling = self.dpi_scaling  # 根據選擇的螢幕 DPI 縮放
        print(f"mouseReleaseEvent scaling={scaling}")
        
        top_left = self.screen_geometry.topLeft()
        print(f"top_left.x()={top_left.x()}, top_left.y()={top_left.y()}")
        
        x = top_left.x()+int((x - top_left.x()) * scaling)
        y = top_left.y()+int((y - top_left.y()) * scaling)

        w = int(w * scaling)
        h = int(h * scaling)
        

        if w > 10 and h > 10:
            self.selected_area = (x, y, w, h)

        self.close()

    def paintEvent(self, event):
        if not self.start_pos or not self.end_pos:
            return

        painter = QPainter(self)
        painter.setPen(QPen(QColor(255, 0, 0), 5, Qt.DashLine))
        
        painter.drawRect(QRect(self.start_pos, self.end_pos))
        


    @staticmethod
    def get_selected_area(screen_geometry, dpi_scaling):
        app = QApplication.instance() or QApplication(sys.argv)
        selector = ScreenSelection(screen_geometry, dpi_scaling)
        while selector.isVisible():
            app.processEvents()
        return selector.selected_area



class RecordingOverlay(QWidget):
    """顯示錄影範圍的透明標記框"""
    def __init__(self, area, dpi_scaling, screen_geometry):
        super().__init__()
        self.dpi_scaling=dpi_scaling
        self.screen_geometry=screen_geometry
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 擴大邊框範圍，避免框線被錄進去
        x, y, w, h = area
        top_left = self.screen_geometry.topLeft()

        x=top_left.x()+int((x-top_left.x())/dpi_scaling)
        y=top_left.y()+int((y-top_left.y())/dpi_scaling)
        w=int(w/dpi_scaling)
        h=int(h/dpi_scaling)
        print(f"drawing ({x}, {y}, {w}, {h})")

        padding = 2  # 增加 3 像素的邊界
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