import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, 
                             QLabel, QStackedLayout, QMainWindow)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QCursor, QTouchEvent

class VerticalPager(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QStackedLayout(self)
        self.current_index = 0
        self.is_animating = False
        
        # 创建几个示例页面
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        for i, color in enumerate(colors):
            page = QWidget()
            page.setStyleSheet(f"background-color: {color}; border-radius: 10px;")
            layout = QVBoxLayout()
            label = QLabel(f"Page {i+1}")
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("font-size: 24px; color: white; font-weight: bold;")
            layout.addWidget(label)
            page.setLayout(layout)
            self.layout.addWidget(page)
        
        self.setMinimumSize(400, 600)
        
    def mousePressEvent(self, event):
        self.start_pos = event.pos()
        super().mousePressEvent(event)
        
    def mouseReleaseEvent(self, event):
        if self.is_animating:
            return
            
        end_pos = event.pos()
        delta_y = end_pos.y() - self.start_pos.y()
        
        # 滑动距离阈值
        if abs(delta_y) > 50:
            if delta_y > 0 and self.current_index > 0:  # 向下滑动，上一页
                self.switch_to_page(self.current_index - 1)
            elif delta_y < 0 and self.current_index < self.layout.count() - 1:  # 向上滑动，下一页
                self.switch_to_page(self.current_index + 1)
        
        super().mouseReleaseEvent(event)
    
    def touchEvent(self, event):
        """处理触摸事件以支持触屏滑动"""
        if self.is_animating:
            return
        
        # 获取触摸点
        touch_points = event.touchPoints()
        if not touch_points:
            return
        
        touch_point = touch_points[0]  # 只处理第一个触摸点
        
        if touch_point.state() == QTouchEvent.TouchPointPressed:
            # 触摸开始，记录起始位置
            self.start_pos = touch_point.pos().toPoint()
        elif touch_point.state() == QTouchEvent.TouchPointReleased:
            # 触摸结束，计算滑动距离
            end_pos = touch_point.pos().toPoint()
            delta_y = end_pos.y() - self.start_pos.y()
            
            # 滑动距离阈值
            if abs(delta_y) > 50:
                if delta_y > 0 and self.current_index > 0:  # 向下滑动，上一页
                    self.switch_to_page(self.current_index - 1)
                elif delta_y < 0 and self.current_index < self.layout.count() - 1:  # 向上滑动，下一页
                    self.switch_to_page(self.current_index + 1)
        
        # 接受事件
        event.accept()
    
    def switch_to_page(self, new_index):
        if self.is_animating or new_index < 0 or new_index >= self.layout.count():
            return
            
        self.is_animating = True
        self.current_index = new_index
        self.layout.setCurrentIndex(new_index)
        self.is_animating = False

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vertical Pager - 上下滑动翻页")
        self.pager = VerticalPager()
        self.setCentralWidget(self.pager)
        self.resize(400, 600)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())