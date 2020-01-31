# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\Codes\pyTyper\QtTyperAbout.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_TyperAboutMainWindow(object):
    def setupUi(self, typerAboutMainWindow):
        typerAboutMainWindow.setObjectName("typerAboutMainWindow")
        typerAboutMainWindow.resize(300, 150)
        self.centralwidget = QtWidgets.QWidget(typerAboutMainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(65, 30, 170, 60))
        font = QtGui.QFont()
        font.setFamily("Harlow Solid Italic")
        font.setPointSize(36)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        typerAboutMainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(typerAboutMainWindow)
        QtCore.QMetaObject.connectSlotsByName(typerAboutMainWindow)

    def retranslateUi(self, typerAboutMainWindow):
        _translate = QtCore.QCoreApplication.translate
        typerAboutMainWindow.setWindowTitle(_translate("typerAboutMainWindow", "pyTyper"))
        self.label.setText(_translate("typerAboutMainWindow", "pyTyper"))