# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainGUI.ui'
#
# Created: Mon Oct 21 15:25:36 2013
#      by: PyQt4 UI code generator 4.10
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_frmMain(object):
    def setupUi(self, frmMain):
        frmMain.setObjectName(_fromUtf8("frmMain"))
        frmMain.resize(800, 600)
        self.tabWidget = QtGui.QTabWidget(frmMain)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 791, 591))
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tabImage = QtGui.QWidget()
        self.tabImage.setObjectName(_fromUtf8("tabImage"))
        self.imgVideo = QtGui.QGraphicsView(self.tabImage)
        self.imgVideo.setGeometry(QtCore.QRect(140, 10, 640, 480))
        self.imgVideo.setResizeAnchor(QtGui.QGraphicsView.AnchorViewCenter)
        self.imgVideo.setObjectName(_fromUtf8("imgVideo"))
        self.cmdCoriander = QtGui.QPushButton(self.tabImage)
        self.cmdCoriander.setGeometry(QtCore.QRect(140, 500, 111, 31))
        self.cmdCoriander.setObjectName(_fromUtf8("cmdCoriander"))
        self.cmdStopVideo = QtGui.QPushButton(self.tabImage)
        self.cmdStopVideo.setGeometry(QtCore.QRect(670, 500, 111, 31))
        self.cmdStopVideo.setObjectName(_fromUtf8("cmdStopVideo"))
        self.cmdStartVideo = QtGui.QPushButton(self.tabImage)
        self.cmdStartVideo.setGeometry(QtCore.QRect(550, 500, 111, 31))
        self.cmdStartVideo.setObjectName(_fromUtf8("cmdStartVideo"))
        self.txtSource = QtGui.QLineEdit(self.tabImage)
        self.txtSource.setGeometry(QtCore.QRect(10, 40, 121, 27))
        self.txtSource.setObjectName(_fromUtf8("txtSource"))
        self.lblSource = QtGui.QLabel(self.tabImage)
        self.lblSource.setGeometry(QtCore.QRect(10, 10, 51, 31))
        self.lblSource.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.lblSource.setObjectName(_fromUtf8("lblSource"))
        self.cmdAddSource = QtGui.QPushButton(self.tabImage)
        self.cmdAddSource.setGeometry(QtCore.QRect(30, 70, 87, 27))
        self.cmdAddSource.setObjectName(_fromUtf8("cmdAddSource"))
        self.cmbConversion = QtGui.QComboBox(self.tabImage)
        self.cmbConversion.setGeometry(QtCore.QRect(370, 500, 171, 27))
        self.cmbConversion.setMaxVisibleItems(5)
        self.cmbConversion.setObjectName(_fromUtf8("cmbConversion"))
        self.lblConversion = QtGui.QLabel(self.tabImage)
        self.lblConversion.setGeometry(QtCore.QRect(280, 500, 81, 31))
        self.lblConversion.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblConversion.setObjectName(_fromUtf8("lblConversion"))
        self.tabWidget.addTab(self.tabImage, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.grbUnfisheye = QtGui.QGroupBox(self.tab_2)
        self.grbUnfisheye.setGeometry(QtCore.QRect(20, 10, 341, 541))
        self.grbUnfisheye.setAlignment(QtCore.Qt.AlignCenter)
        self.grbUnfisheye.setFlat(False)
        self.grbUnfisheye.setCheckable(False)
        self.grbUnfisheye.setObjectName(_fromUtf8("grbUnfisheye"))
        self.cmdCalibrateDistortion = QtGui.QPushButton(self.grbUnfisheye)
        self.cmdCalibrateDistortion.setGeometry(QtCore.QRect(130, 340, 87, 27))
        self.cmdCalibrateDistortion.setObjectName(_fromUtf8("cmdCalibrateDistortion"))
        self.imgDistortion = QtGui.QGraphicsView(self.grbUnfisheye)
        self.imgDistortion.setGeometry(QtCore.QRect(10, 30, 320, 240))
        self.imgDistortion.setObjectName(_fromUtf8("imgDistortion"))
        self.txtPatternXMax = QtGui.QLineEdit(self.grbUnfisheye)
        self.txtPatternXMax.setGeometry(QtCore.QRect(110, 440, 41, 27))
        self.txtPatternXMax.setObjectName(_fromUtf8("txtPatternXMax"))
        self.txtPatternYMax = QtGui.QLineEdit(self.grbUnfisheye)
        self.txtPatternYMax.setGeometry(QtCore.QRect(110, 470, 41, 27))
        self.txtPatternYMax.setObjectName(_fromUtf8("txtPatternYMax"))
        self.lblPatternXMax = QtGui.QLabel(self.grbUnfisheye)
        self.lblPatternXMax.setGeometry(QtCore.QRect(10, 440, 91, 21))
        self.lblPatternXMax.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblPatternXMax.setObjectName(_fromUtf8("lblPatternXMax"))
        self.cmdFindPattern = QtGui.QPushButton(self.grbUnfisheye)
        self.cmdFindPattern.setGeometry(QtCore.QRect(110, 510, 131, 27))
        self.cmdFindPattern.setObjectName(_fromUtf8("cmdFindPattern"))
        self.lblPatternYMax = QtGui.QLabel(self.grbUnfisheye)
        self.lblPatternYMax.setGeometry(QtCore.QRect(10, 470, 91, 21))
        self.lblPatternYMax.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblPatternYMax.setObjectName(_fromUtf8("lblPatternYMax"))
        self.txtPatternXMin = QtGui.QLineEdit(self.grbUnfisheye)
        self.txtPatternXMin.setGeometry(QtCore.QRect(280, 440, 41, 27))
        self.txtPatternXMin.setObjectName(_fromUtf8("txtPatternXMin"))
        self.lblPatternXMin = QtGui.QLabel(self.grbUnfisheye)
        self.lblPatternXMin.setGeometry(QtCore.QRect(180, 440, 91, 21))
        self.lblPatternXMin.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblPatternXMin.setObjectName(_fromUtf8("lblPatternXMin"))
        self.txtPatternYMin = QtGui.QLineEdit(self.grbUnfisheye)
        self.txtPatternYMin.setGeometry(QtCore.QRect(280, 470, 41, 27))
        self.txtPatternYMin.setObjectName(_fromUtf8("txtPatternYMin"))
        self.lblPatternYMin = QtGui.QLabel(self.grbUnfisheye)
        self.lblPatternYMin.setGeometry(QtCore.QRect(180, 470, 91, 21))
        self.lblPatternYMin.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblPatternYMin.setObjectName(_fromUtf8("lblPatternYMin"))
        self.lblPatternY = QtGui.QLabel(self.grbUnfisheye)
        self.lblPatternY.setGeometry(QtCore.QRect(180, 280, 91, 21))
        self.lblPatternY.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblPatternY.setObjectName(_fromUtf8("lblPatternY"))
        self.txtPatternY = QtGui.QLineEdit(self.grbUnfisheye)
        self.txtPatternY.setGeometry(QtCore.QRect(280, 280, 41, 27))
        self.txtPatternY.setObjectName(_fromUtf8("txtPatternY"))
        self.txtPatternX = QtGui.QLineEdit(self.grbUnfisheye)
        self.txtPatternX.setGeometry(QtCore.QRect(110, 280, 41, 27))
        self.txtPatternX.setObjectName(_fromUtf8("txtPatternX"))
        self.lblPatternX = QtGui.QLabel(self.grbUnfisheye)
        self.lblPatternX.setGeometry(QtCore.QRect(10, 280, 91, 21))
        self.lblPatternX.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblPatternX.setObjectName(_fromUtf8("lblPatternX"))
        self.txtCalibrationFrames = QtGui.QLineEdit(self.grbUnfisheye)
        self.txtCalibrationFrames.setGeometry(QtCore.QRect(280, 310, 41, 27))
        self.txtCalibrationFrames.setObjectName(_fromUtf8("txtCalibrationFrames"))
        self.lblCalibrationFrames = QtGui.QLabel(self.grbUnfisheye)
        self.lblCalibrationFrames.setGeometry(QtCore.QRect(20, 310, 251, 21))
        self.lblCalibrationFrames.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblCalibrationFrames.setObjectName(_fromUtf8("lblCalibrationFrames"))
        self.grbTransformation = QtGui.QGroupBox(self.tab_2)
        self.grbTransformation.setGeometry(QtCore.QRect(420, 10, 341, 541))
        self.grbTransformation.setAlignment(QtCore.Qt.AlignCenter)
        self.grbTransformation.setFlat(False)
        self.grbTransformation.setCheckable(False)
        self.grbTransformation.setObjectName(_fromUtf8("grbTransformation"))
        self.cmdCCalibrateTransformation = QtGui.QPushButton(self.grbTransformation)
        self.cmdCCalibrateTransformation.setGeometry(QtCore.QRect(130, 280, 87, 27))
        self.cmdCCalibrateTransformation.setObjectName(_fromUtf8("cmdCCalibrateTransformation"))
        self.imgTransformation = QtGui.QGraphicsView(self.grbTransformation)
        self.imgTransformation.setGeometry(QtCore.QRect(10, 30, 320, 240))
        self.imgTransformation.setObjectName(_fromUtf8("imgTransformation"))
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))

        self.retranslateUi(frmMain)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(frmMain)

    def retranslateUi(self, frmMain):
        frmMain.setWindowTitle(_translate("frmMain", "mrVision", None))
        self.cmdCoriander.setText(_translate("frmMain", "Start Coriander", None))
        self.cmdStopVideo.setText(_translate("frmMain", "S&top", None))
        self.cmdStartVideo.setText(_translate("frmMain", "&Start", None))
        self.txtSource.setText(_translate("frmMain", "0", None))
        self.lblSource.setText(_translate("frmMain", "Source:", None))
        self.cmdAddSource.setText(_translate("frmMain", "&Add", None))
        self.lblConversion.setText(_translate("frmMain", "Conversion:", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabImage), _translate("frmMain", "Video", None))
        self.grbUnfisheye.setTitle(_translate("frmMain", "Distortion", None))
        self.cmdCalibrateDistortion.setText(_translate("frmMain", "&Calibrate", None))
        self.txtPatternXMax.setText(_translate("frmMain", "20", None))
        self.txtPatternYMax.setText(_translate("frmMain", "20", None))
        self.lblPatternXMax.setText(_translate("frmMain", "Pattern X max:", None))
        self.cmdFindPattern.setText(_translate("frmMain", "&Find chess pattern", None))
        self.lblPatternYMax.setText(_translate("frmMain", "Pattern Y max:", None))
        self.txtPatternXMin.setText(_translate("frmMain", "3", None))
        self.lblPatternXMin.setText(_translate("frmMain", "Pattern X min:", None))
        self.txtPatternYMin.setText(_translate("frmMain", "3", None))
        self.lblPatternYMin.setText(_translate("frmMain", "Pattern Y min:", None))
        self.lblPatternY.setText(_translate("frmMain", "Pattern Y:", None))
        self.txtPatternY.setText(_translate("frmMain", "3", None))
        self.txtPatternX.setText(_translate("frmMain", "20", None))
        self.lblPatternX.setText(_translate("frmMain", "Pattern X:", None))
        self.txtCalibrationFrames.setText(_translate("frmMain", "10", None))
        self.lblCalibrationFrames.setText(_translate("frmMain", "No. of frames for calibration:", None))
        self.grbTransformation.setTitle(_translate("frmMain", "Transformation", None))
        self.cmdCCalibrateTransformation.setText(_translate("frmMain", "Calibra&te", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("frmMain", "Calibration", None))

