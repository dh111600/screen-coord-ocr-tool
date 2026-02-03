import sys
import re
import pytesseract
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QTextEdit, QVBoxLayout, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QClipboard
from PIL import Image
import mss
import io

# 识别和转换函数
def recognize_coords_from_screen():
    try:
        with mss.mss() as sct:
            screenshot = sct.grab(sct.monitors[0])
            img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
        text = pytesseract.image_to_string(img, lang='eng+chi_sim')
        # 只提取纯数字,数字格式
        pattern = r'\b(\d+),(\d+)\b'
        matches = re.findall(pattern, text)
        results = [f"{x}.{y}" for x, y in matches]
        return results, len(matches)
    except Exception as e:
        return str(e), -1

class CoordApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('坐标识别工具')
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setFixedSize(320, 320)
        self.history = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.btn_recognize = QPushButton('识别屏幕坐标文字')
        self.btn_copy = QPushButton('复制第一个坐标')
        self.result_area = QTextEdit()
        self.result_area.setReadOnly(True)
        layout.addWidget(self.btn_recognize)
        layout.addWidget(self.btn_copy)
        layout.addWidget(self.result_area)
        self.setLayout(layout)
        self.btn_recognize.clicked.connect(self.on_recognize)
        self.btn_copy.clicked.connect(self.on_copy)

    def on_recognize(self):
        results, count = recognize_coords_from_screen()
        if count == -1:
            QMessageBox.warning(self, '错误', f'OCR识别失败: {results}')
            return
        if count == 0:
            QMessageBox.information(self, '提示', '未找到目标坐标文字')
            self.result_area.setText('')
            return
        self.history = results
        self.result_area.setText('\n'.join(results))
        QMessageBox.information(self, '识别完成', f'共找到 {count} 个坐标:\n' + '\n'.join(results))

    def on_copy(self):
        if not self.history:
            QMessageBox.information(self, '提示', '暂无有效坐标可复制')
            return
        clipboard = QApplication.clipboard()
        clipboard.setText(self.history[0], QClipboard.Clipboard)
        QMessageBox.information(self, '复制成功', f'已复制: {self.history[0]}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = CoordApp()
    win.show()
    sys.exit(app.exec_())
