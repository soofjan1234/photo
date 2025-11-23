import sys
import os
import json
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, 
                             QLabel, QStackedLayout, QMainWindow, QHBoxLayout)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QCursor, QTouchEvent, QPixmap
from slide import SlideAnimator


class VerticalPager(QWidget):
    def __init__(self, image_folder=None):
        super().__init__()
        self.layout = QStackedLayout(self)
        self.current_index = 0
        self.is_animating = False
        self.animator = SlideAnimator(self)
        self.image_paths = []  # 存储图片路径

        # 如果提供了图片文件夹路径，则加载图片
        if image_folder and os.path.exists(image_folder):
            self.load_images_from_folder(image_folder)
        else:
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
    
    def load_images_from_folder(self, folder_path):
        """从指定文件夹加载图片"""
        # 支持的图片格式
        supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
        
        # 获取文件夹中的所有图片文件
        for filename in os.listdir(folder_path):
            ext = os.path.splitext(filename)[1].lower()
            if ext in supported_formats:
                self.image_paths.append(os.path.join(folder_path, filename))
        
        # 为每个图片创建页面
        for image_path in self.image_paths:
            page = QWidget()
            layout = QVBoxLayout()
            # 设置布局无边距
            layout.setContentsMargins(0, 0, 0, 0)
            
            # 创建QLabel显示图片
            image_label = QLabel()
            image_label.setAlignment(Qt.AlignCenter)
            
            # 加载并显示图片，宽度与窗口宽度匹配
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                # 使用窗口宽度（如果可用）或默认宽度
                target_width = self.width() if self.width() > 0 else 400
                # 计算保持比例的高度并转换为整数
                target_height = int(pixmap.height() * target_width / pixmap.width())
                scaled_pixmap = pixmap.scaled(
                    target_width,
                    target_height,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                image_label.setPixmap(scaled_pixmap)
                image_label.setMinimumSize(scaled_pixmap.size())
                image_label.setMaximumSize(scaled_pixmap.size())
                
            layout.addWidget(image_label)
            page.setLayout(layout)
            self.layout.addWidget(page)
    
    def resizeEvent(self, event):
        """窗口大小变化时重新调整图片大小，使图片宽度与窗口宽度匹配"""
        for i in range(self.layout.count()):
            page = self.layout.widget(i)
            if page and page.layout() and page.layout().count() > 0:
                image_label = page.layout().itemAt(0).widget()
                if isinstance(image_label, QLabel) and hasattr(image_label, 'pixmap') and image_label.pixmap():
                    # 获取窗口宽度
                    window_width = self.width()
                    # 调整图片大小，宽度与窗口宽度匹配，保持比例
                    # 计算保持比例的高度并转换为整数
                    target_height = int(image_label.pixmap().height() * window_width / image_label.pixmap().width())
                    scaled_pixmap = image_label.pixmap().scaled(
                        window_width, 
                        target_height,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                    image_label.setPixmap(scaled_pixmap)
                    # 设置label的尺寸策略以适应内容
                    image_label.setMinimumSize(scaled_pixmap.size())
                    image_label.setMaximumSize(scaled_pixmap.size())
        super().resizeEvent(event)
        
    def mousePressEvent(self, event):
        self.start_pos = event.pos()
        super().mousePressEvent(event)
        
    def mouseReleaseEvent(self, event):
        if self.is_animating:
            return
            
        end_pos = event.pos()
        delta_y = end_pos.y() - self.start_pos.y()
        
        # 滑动距离阈值
        # 滑动距离阈值
        if abs(delta_y) > 50:
            if delta_y > 0:  # 向下滑动
                new_index = (self.current_index - 1) % self.layout.count()
                self.switch_to_page(new_index)

            elif delta_y < 0:  # 向上滑动，下一页
                new_index = (self.current_index + 1) % self.layout.count()
                self.switch_to_page(new_index)
        
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
                if delta_y > 0:  # 向下滑动
                    new_index = (self.current_index - 1) % self.layout.count()
                    self.switch_to_page(new_index)

                elif delta_y < 0:  # 向上滑动，下一页
                    new_index = (self.current_index + 1) % self.layout.count()
                    self.switch_to_page(new_index)
        
        # 接受事件
        event.accept()
    
    def switch_to_page(self, new_index):
        if self.is_animating:
            return

        count = self.layout.count()
        old_widget = self.layout.currentWidget()
        new_widget = self.layout.widget(new_index)

        # 判断方向（处理循环）
        if (new_index == (self.current_index + 1) % count):
            direction = "up"
        else:
            direction = "down"

        self.is_animating = True

        # 执行动画
        anim = self.animator.slide(old_widget, new_widget, direction)

        def finish():
            self.layout.setCurrentIndex(new_index)
            self.current_index = new_index
            old_widget.hide()
            self.is_animating = False

        anim.finished.connect(finish)



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("三栏图片浏览器 - 上下滑动翻页")
        
        # 加载配置文件
        self.config = self.load_config()
        
        # 创建主窗口部件和水平布局
        central_widget = QWidget()
        self.main_layout = QHBoxLayout(central_widget)
        self.main_layout.setSpacing(0)  # 区域之间没有间隔
        self.main_layout.setContentsMargins(0, 0, 0, 0)  # 无边距
        
        # 根据配置创建三个垂直分页器
        self.pagers = []
        # 使用config.json中的键名
        album_keys = ['album_left', 'album_middle', 'album_right']
        for key in album_keys:
            # 获取对应的相册配置
            album_config = self.config.get(key, {})
            image_folder = album_config.get('path', None)
            
            # 创建分页器
            pager = VerticalPager(image_folder)
            self.pagers.append(pager)
            self.main_layout.addWidget(pager)
        
        # 设置中央部件
        self.setCentralWidget(central_widget)
        
        # 设置窗口大小
        self.resize(1200, 600)  # 三栏布局，每个分页器大约400x600
        # 设置全屏显示
        self.showFullScreen()
    
    def load_config(self):
        """加载配置文件"""
        config_file = 'config.json'
        
        # 空的默认配置字典
        user_config = {}
        
        # 如果配置文件存在，读取配置
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    return user_config
            except Exception as e:
                print(f"读取配置文件出错: {e}")
                # 返回空字典而不创建默认配置
        return user_config
    
    def save_config(self, config):
        """保存配置到文件"""
        config_file = 'config.json'
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            print(f"配置文件已创建: {config_file}")
        except Exception as e:
            print(f"保存配置文件出错: {e}")

if __name__ == '__main__':
    # 设置触摸屏支持（必须在创建QApplication之前）
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    
    app = QApplication(sys.argv)
    window = MainWindow()
    # 窗口已经在初始化时设置为全屏，这里不需要再次调用show()
    # window.show()  # 注释掉普通显示方法
    sys.exit(app.exec_())