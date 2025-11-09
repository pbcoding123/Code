import asyncio
import edge_tts
from PyQt5.QtCore import Qt
import iconqrc
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *
from qasync import asyncSlot, QEventLoop
import sys

voice_list = [
    "zh-CN-XiaochenMultilingualNeural      Female",
    "zh-CN-XiaochenNeural                  Female",
    "zh-CN-XiaohanNeural                   Female",
    "zh-CN-XiaomengNeural                  Female",
    "zh-CN-XiaomoNeural                    Female",
    "zh-CN-XiaoqiuNeural                   Female",
    "zh-CN-XiaorouNeural                   Female",
    "zh-CN-XiaoruiNeural                   Female",
    "zh-CN-XiaoshuangNeural                Female",
    "zh-CN-XiaoxiaoDialectsNeural          Female",
    "zh-CN-XiaoxiaoMultilingualNeural      Female",
    "zh-CN-XiaoxiaoNeural                  Female",
    "zh-CN-XiaoyanNeural                   Female",
    "zh-CN-XiaoyiNeural                    Female",
    "zh-CN-XiaoyouNeural                   Female",
    "zh-CN-XiaoyuMultilingualNeural        Female",
    "zh-CN-XiaozhenNeural                  Female",
    "zh-CN-YunfengNeural                   Male",
    "zh-CN-YunhaoNeural                    Male",
    "zh-CN-YunjianNeural                   Male",
    "zh-CN-YunjieNeural                    Male",
    "zh-CN-YunxiNeural                     Male",
    "zh-CN-YunxiaNeural                    Male",
    "zh-CN-YunxiaoMultilingualNeural       Male",
    "zh-CN-YunyangNeural                   Male",
    "zh-CN-YunyeNeural                     Male",
    "zh-CN-YunyiMultilingualNeural         Male",
    "zh-CN-YunzeNeural                     Male",
    "zh-CN-henan-YundengNeural             Male",
    "zh-CN-liaoning-XiaobeiNeural          Female",
    "zh-CN-shaanxi-XiaoniNeural            Female",
    "zh-CN-shandong-YunxiangNeural         Male",
    "zh-CN-sichuan-YunxiNeural             Male",
    "zh-HK-HiuGaaiNeural                   Female",
    "zh-HK-HiuMaanNeural                   Female",
    "zh-HK-WanLungNeural                   Male",
    "zh-TW-HsiaoChenNeural                 Female",
    "zh-TW-HsiaoYuNeural                   Female",
    "zh-TW-YunJheNeural                    Male"
]

advancing = False
voice = 21

class Advance(QDialog):
    def closeEvent(self, evt):
        global advancing
        advancing = False
        super().closeEvent(evt)

    def __init__(self, parent:QWidget):
        super().__init__(parent)
        global advancing, voice
        advancing = True
        self.setWindowTitle("高级设置")
        self.setWindowIcon(QIcon(":/icon.ico"))
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setModal(True)
        ly = QFormLayout(self)
        cbb = QComboBox()
        cbb.addItems(voice_list)
        cbb.setCurrentIndex(voice)
        cbb.currentIndexChanged.connect(self.cbbchange)
        ly.addRow(QLabel("朗读者:"), cbb)
        btn = QPushButton("确定")
        btn.clicked.connect(self.close)
        lay = QHBoxLayout()
        lay.addStretch(1)
        lay.addWidget(btn)
        ly.addRow(lay)
        self.show()

    def cbbchange(self, idx):
        global voice
        voice = idx

class convertUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.show()
    
    def initUI(self):
        self.setWindowTitle("文本转语音")
        self.setWindowIcon(QIcon(":/icon.ico"))
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("待转换的文本:"))
        self.edt = QTextEdit()
        self.edt.setPlaceholderText("...")
        layout.addWidget(self.edt)
        self.saveto = QLabel("保存到:")
        layout.addWidget(self.saveto)
        savebnt = QPushButton("选择保存路径")
        savebnt.clicked.connect(self.saveas)
        conv = QPushButton("转换")
        conv.clicked.connect(self.start_convert)
        adv = QPushButton("高级设置")
        adv.clicked.connect(self.advanced)
        helping = QPushButton("关于")
        helping.clicked.connect(self.help)
        sublay1 = QHBoxLayout()
        sublay1.addWidget(savebnt)
        sublay1.addWidget(conv)
        sublay2 = QHBoxLayout()
        sublay2.addWidget(adv)
        sublay2.addWidget(helping)
        layout.addLayout(sublay1)
        layout.addLayout(sublay2)

    def saveas(self):
        file = QFileDialog.getSaveFileName(self, "保存", ".\\", "音频文件 (*.mp3)")[0]
        self.saveto.setText("保存到:"+file)

    def start_convert(self):
        if len(self.edt.toPlainText())==0:
            QMessageBox.information(self, "转换", "内容为空", QMessageBox.Ok)
            return
        if len(self.saveto.text())<=4:
            QMessageBox.information(self, "转换", "请选择保存路径", QMessageBox.Ok)
            return

        asyncio.ensure_future(self.convert())

    def advanced(self):
        try:
            if not advancing:
                win888 = Advance(self)
        except Exception as e:
            print(f"创建高级设置窗口时出错: {e}")
            QMessageBox.warning(self, "错误", f"无法打开高级设置窗口: {e}")

    @asyncSlot()
    async def convert(self):
        global voice
        vt = QDialog()
        vt.setWindowTitle("转换")
        ly = QVBoxLayout(vt)
        if len(self.edt.toPlainText())<=20:
            ly.addWidget(QLabel("文本:"+self.edt.toPlainText()))
        else:
            ly.addWidget(QLabel("文本:"+self.edt.toPlainText()[:17]+"..."))
        ly.addWidget(QLabel("朗读者:"+voice_list[voice]))
        state = QLabel("当前状态:")
        ly.addWidget(state)
        vt.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        vt.setWindowIcon(QIcon(":/icon.ico"))
        vt.show()
        state.setText("当前状态:正在转换")
        await asyncio.sleep(0.3)
        voi = voice_list[voice]
        voi = voi[:voi.find(" ")]
        cc = edge_tts.Communicate(self.edt.toPlainText(), voi)
        state.setText("当前状态:正在导出")
        await cc.save(self.saveto.text()[4:])
        state.setText("当前状态:已完成")
        QMessageBox.information(vt, "转换", "已完成", QMessageBox.Ok)
        await asyncio.sleep(2)
        vt.close()

    def help(self):
        print("helping...")


app = QApplication(sys.argv)
loop = QEventLoop(app)
asyncio.set_event_loop(loop)
win = convertUI()
with loop:
    loop.run_forever()
