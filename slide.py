from PyQt5.QtCore import QObject, QRect, QPoint, QPropertyAnimation, QEasingCurve

class SlideAnimator(QObject):
    def __init__(self, container):
        super().__init__()
        self.container = container  # 要做动画的父 QWidget

    def slide(self, old_widget, new_widget, direction="up", duration=300):
        """
        direction: "up"（下一页） 或 "down"（上一页）
        """
        h = self.container.height()

        if direction == "up":
            start_pos_new = QPoint(0, h)
            end_pos_old = QPoint(0, -h)
        else:
            start_pos_new = QPoint(0, -h)
            end_pos_old = QPoint(0, h)

        # 先把 new_widget 放到正确的初始位置
        new_widget.setGeometry(0, start_pos_new.y(),
                               self.container.width(), h)
        new_widget.show()

        # old_widget 动画
        anim_old = QPropertyAnimation(old_widget, b"pos")
        anim_old.setDuration(duration)
        anim_old.setStartValue(old_widget.pos())
        anim_old.setEndValue(end_pos_old)
        anim_old.setEasingCurve(QEasingCurve.InOutQuad)

        # new_widget 动画
        anim_new = QPropertyAnimation(new_widget, b"pos")
        anim_new.setDuration(duration)
        anim_new.setStartValue(start_pos_new)
        anim_new.setEndValue(QPoint(0, 0))
        anim_new.setEasingCurve(QEasingCurve.InOutQuad)

        # 启动动画
        anim_old.start()
        anim_new.start()

        # 防止动画被回收
        self.anim_old = anim_old
        self.anim_new = anim_new

        return anim_new
