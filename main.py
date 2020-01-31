import sys,sqlite3,keyboard,threading
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from Ui_TyperAbout import Ui_TyperAboutMainWindow

__author__ = 'kdxcxs'
__version__ = '0.1.2'

def getTitles():
    db_connection = sqlite3.connect('D:\\Codes\\pyTyper\\pyTyper.db')
    root_cursor = db_connection.cursor()
    listTitles = list(root_cursor.execute('SELECT title FROM itemList;'))
    titleMenu = []
    for title in listTitles:
        titleMenu.append(title[0])
    db_connection.close()
    return titleMenu

def getValue(title):
    try:
        db_connection = sqlite3.connect('D:\\Codes\\pyTyper\\pyTyper.db')
        root_cursor = db_connection.cursor()
        value = list(root_cursor.execute('SELECT value FROM itemList WHERE title="{title}";'.format(title=title.replace('\"','\\\"'))))[0][0]
    except BaseException as error: # 捕获所有异常
        value = [['None']]
    finally:
        db_connection.close()
        return value

class TyperValueTyper(object):
    def __init__(self, titleGetter): # 将titleGetter指向TrayIcon类的toolTip方法从而在快捷键触发时获取当前项目的title
       keyboard.add_hotkey('ctrl+alt+x',self.typeValue)
       self.titleGetter = titleGetter
    
    def typeValue(self):
        threading.Thread(target=keyboard.write(getValue(self.titleGetter()[8:]))).start()

class QtTyperAbout(QMainWindow):
    def __init__(self, parent=None):
        super(QtTyperAbout, self).__init__(parent)
        self.aboutUi = Ui_TyperAboutMainWindow()
        self.aboutUi.setupUi(self)
        self.setWindowIcon(QIcon("pytyper.png"))
    
    def closeEvent(self, event): # 重写closeEvent方法,否则关闭关于窗口整个程序都会退出
        self.hide()
        event.ignore()

class TyperChangeItemAction(QAction):
    def __init__(self, text, parent=None):
        super(TyperChangeItemAction, self).__init__(text, parent)
        self.trayIcon = parent
        self.triggered.connect(self.changeTyperItem)
    
    def changeTyperItem(self):
        self.trayIcon.changeItem(self.text())

class TrayIcon(QSystemTrayIcon):
    def __init__(self, parent=None):
        super(TrayIcon, self).__init__(parent)
        self.setToolTip('pyTyper|'+getTitles()[0]) # 当鼠标悬浮到托盘图标时显示的文本
        self.createMenu()
        self.show()
        self.valueTyper = TyperValueTyper(self.toolTip)

    def createMenu(self):
        self.mainMenu = QMenu()
        self.itemChangingMenu = QMenu('切换')
        self.refreshListAction = QAction('刷新',self,triggered=self.refreshItemList)
        self.aboutAction = QAction("关于", self,triggered=self.showAbout)
        self.quitAction = QAction("退出", self, triggered=self.quit)

        for title in getTitles():
            self.itemChangingMenu.addAction(TyperChangeItemAction(title,self))
        
        self.mainMenu.addMenu(self.itemChangingMenu)
        self.mainMenu.addAction(self.refreshListAction)
        self.mainMenu.addAction(self.aboutAction)
        self.mainMenu.addAction(self.quitAction)
        self.setContextMenu(self.mainMenu)

        # 设置图标
        self.setIcon(QIcon("pytyper.png"))
        self.icon = self.MessageIcon()

        # 初始化关于界面
        self.aboutWindow = QtTyperAbout()

    def changeItem(self,title):
        self.setToolTip('pyTyper|'+title)
        self.showMsg('已成功切换到'+title)

    def refreshItemList(self):
        self.itemChangingMenu.clear()
        for title in getTitles():
            self.itemChangingMenu.addAction(TyperChangeItemAction(title,self))
        self.showMsg('刷新成功')

    def showAbout(self):
        self.aboutWindow.show()

    def showMsg(self,msg):
        self.showMessage("pyTyper", msg, self.icon)

    def quit(self):
        app.quit()
        sys.exit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pyTyperTrayIcon = TrayIcon()
    sys.exit(app.exec_())        # exec_()方法的作用是“进入程序的主循环直到exit()被调