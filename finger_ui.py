#!/usr/bin/python3
# -*- coding: utf-8 -*-
import time
import sys
import serial
#from PyQt5.QtWidgets import QInputDialog,QWidget, QPushButton, QApplication,QMessageBox
from PyQt5.QtCore import *#QCoreApplication
from PyQt5.QtGui import *#QIcon,QPalette,QBrush,QPixmap,QColor
from PyQt5.QtWidgets import *#QWidget,QLabel,QPushButton,QGridLayout,QApplication
import RPi.GPIO as GPIO
#from PyQt5.QtCore import QDate, QTime, QDateTime, Qt
import fingerprint
import password
serialPort="/dev/ttyAMA0" #串口6
baudRate=57600 #波特率
GPIO.setmode(GPIO.BOARD)
GPIO.setup(40, GPIO.OUT)		
class Example(QWidget):
	def __init__(self):
		self.ID = 0
		super().__init__()
		self.ser = serial.Serial(serialPort, baudRate, timeout=0.5)
		self.setMinimumSize(40, 30)
		self.initUI()
		GPIO.output(40, GPIO.LOW)
	def initUI(self):
		self.lcd = QLCDNumber()      
		self.lcd.setDigitCount(9)      
		self.lcd.setMode(QLCDNumber.Dec)
		self.lcd.setSegmentStyle(QLCDNumber.Flat)
		self.lcd.display(time.strftime("%X",time.localtime()))

		#新建一个QTimer对象        
		self.timer = QTimer()      
		self.timer.setInterval(1000)       
		self.timer.start()

		# 信号连接到槽       
		self.timer.timeout.connect(self.onTimerOut)

		self.font = QFont()
		self.font.setFamily('微软雅黑')
		self.font.setBold(True)
		self.font.setPointSize(24)
		self.font.setWeight(90)

		self.icon = QIcon()
		self.icon.addPixmap(QPixmap("finger.png"), QIcon.Normal, QIcon.Off)
		self.finger= QPushButton('指纹解锁', self)
		self.finger.setFont(self.font)
		self.finger.setIcon(self.icon)
		self.finger.setIconSize(QSize(80, 80))
		self.finger.clicked.connect(self.finger_buttonClicked)
		self.finger.resize(600,100)
		self.finger.move(0, 440)

		self.icon = QIcon()
		self.icon.addPixmap(QPixmap("close.png"), QIcon.Normal, QIcon.Off)
		self.passwd = QPushButton('密码解锁', self)
		self.passwd.setFont(self.font)
		self.passwd.setIcon(self.icon)
		self.passwd.setIconSize(QSize(80, 80))
		self.passwd.clicked.connect(self.password_buttonClicked)
		self.passwd.resize(600,100)
		self.passwd.move(0, 560)

		layout = QVBoxLayout()
		layout.addWidget(self.lcd)		
		self.setLayout(layout)
		self.lcd.setGeometry(0, 30, 600, 400)

		layout.addWidget(self.finger)
		self.setLayout(layout)
		self.finger.setGeometry(0, 30, 600, 100)

		layout.addWidget(self.passwd)
		self.setLayout(layout)
		self.passwd.setGeometry(0, 30, 600, 100)

		self.setGeometry(0, 30, 600, 300)
		self.setWindowTitle('指纹识别门禁')
		self.show()
		self.setWindowIcon(QIcon('logo.png'))
		
	# 定义槽
	def onTimerOut(self):        
		self.lcd.display(time.strftime("%X",time.localtime()))
		
	def finger_buttonClicked(self): 
		text, ok = QInputDialog.getText(self, '指纹锁','请选择功能：\n1.录入指纹\n2.身份验证\n3.删除ID=x起的n枚指纹\n4.清空指纹库')
		if ok and text!='' and text!=' ' and text!='  ' and text!='   ' and text!='    'and text!='     ':
			self.n=str(text)
			print(self.n)
			# IDbox = QMessageBox(QMessageBox.Warning, self.tr("提示"), self.tr("请输入ID："), QMessageBox.NoButton, self)
			# IDbox.exec_()
			if self.n == '1':
				IDbox = QMessageBox(QMessageBox.Warning, self.tr("提示"), self.tr("请输入指纹！"), QMessageBox.NoButton, self)
				IDbox.exec_()
				self.add=fingerprint.ADD_FINGERPRINT(self.ser,self.ID)
				if self.add == 1:
					addbox = QMessageBox(QMessageBox.Warning, self.tr("提示"), self.tr("已输入指纹！ID为%s"%self.ID), QMessageBox.NoButton, self)
					addbox.exec_()
					self.ID = self.ID + 1
				else:
					addbox = QMessageBox(QMessageBox.Warning, self.tr("提示"), self.tr("输入指纹失败！"), QMessageBox.NoButton, self)
					addbox.exec_()
			if self.n == '2':
				checkbox = QMessageBox(QMessageBox.Warning, self.tr("提示"), self.tr("请刷指纹！"), QMessageBox.NoButton, self)
				checkbox.exec_()
				self.check,self.id = fingerprint.CHECK_FINGERPRINT(self.ser)
				if self.check == 1:
					checkscbox = QMessageBox(QMessageBox.Warning, self.tr("提示"), self.tr("输入指纹正确！ID为%s"%self.id), QMessageBox.NoButton, self)
					checkscbox.exec_()
					GPIO.output(40, GPIO.HIGH)
					hybox = QMessageBox(QMessageBox.Information, self.tr("欢迎"), self.tr("代表世界欢迎主人回来！！"), QMessageBox.NoButton, self)
					hybox.exec_()
				elif self.check == 0:
					noIDbox = QMessageBox(QMessageBox.Warning, self.tr("提示"), self.tr("身份验证错误！指纹库中没有匹配的身份！！"), QMessageBox.NoButton, self)
					noIDbox.exec_()
				elif self.check == 2:
					nodatebox = QMessageBox(QMessageBox.Warning, self.tr("提示"), self.tr("数据收包错误！"), QMessageBox.NoButton, self)
					nodatebox.exec_()
			if self.n == '3':
				self.delnum = 0
				text, ok = QInputDialog.getText(self, '删除提示','请输入要删除的起始ID和连续删除的指纹数目n(注意：格式为ID|n)')
				if ok and text=='' or text==' ' or text=='  ' or text=='   ' or text=='    'or text=='     ':
					delbox = QMessageBox(QMessageBox.Warning, self.tr("提示"), self.tr("输入要删除的指纹ID！"), QMessageBox.NoButton, self)
					delbox.exec_()
					
					
				if ok and text!='' and text!=' ' and text!='  ' and text!='   ' and text!='    'and text!='     ':
					self.n=str(text)
					print(self.n)
					self.list = self.n.split('|')
					self.ID = int(self.list[0])
					self.delete_num = int(self.list[1])
					self.delnum = 0
					self.delnum = fingerprint.DELETE_FINGERPRINTS( self.ser,self.ID,self.delete_num )
				if self.delnum == 1:
					self.delnum = 0
					delbox = QMessageBox(QMessageBox.Warning, self.tr("删除提示"), self.tr("删除指纹成功！"), QMessageBox.NoButton, self)
					delbox.exec_()
			if self.n == '4':
				if fingerprint.CLEAR_LIBRARY(self.ser) == 1:
					self.ID = 0
					IDbox = QMessageBox(QMessageBox.Warning, self.tr("提示"), self.tr("指纹库已经清空！"), QMessageBox.NoButton, self)
					IDbox.exec_()
					
	def password_buttonClicked(self):
		text, ok = QInputDialog.getText(self, '密码锁','请选择功能：\n1.密码解锁\n2.修改密码')
		if ok and text!='' and text!=' ' and text!='  ' and text!='   ' and text!='    'and text!='     ':
			self.n=str(text)
			print(self.n)
			if self.n == '1':
				text, ok = QInputDialog.getText(self, '密码解锁','请输入密码：')
				if ok and text!='' and text!=' ' and text!='  ' and text!='   ' and text!='    'and text!='     ':
					self.passwd=str(text)
					print(self.passwd)
				with open('passwd.txt', 'r') as f:
					self.pw_r = f.read()
					f.close()
					print(self.pw_r)
				if self.passwd == self.pw_r:
					self.passwd=" "
					GPIO.output(40, GPIO.HIGH)
					hybox = QMessageBox(QMessageBox.Information, self.tr("欢迎"), self.tr("代表世界欢迎主人回来！！"), QMessageBox.NoButton, self)
					hybox.exec_()
				else:
					self.passwd=" "
					QMessageBox.critical(self,"警告",self.tr("密码错误!"))  
			if self.n == '2':
				text, ok = QInputDialog.getText(self, '修改','请输入旧密码：')
				if ok and text!='' and text!=' ' and text!='  ' and text!='   ' and text!='    'and text!='     ':
					self.passwd=str(text)
					print(self.passwd)
					with open('passwd.txt', 'r') as f:
						self.pw_r = f.read()
						f.close()
					new = 1
				else:
					new = 0
					QMessageBox.critical(self,"警告",self.tr("请输入密码!"))
				if new == 1:    
					if self.passwd == self.pw_r:
						text, ok = QInputDialog.getText(self, '修改','请输入新密码：')
						if ok and text!='' and text!=' ' and text!='  ' and text!='   ' and text!='    'and text!='     ':
							self.npasswd=str(text)
							print(self.npasswd)
						else:
							self.npasswd="a"
						text, ok = QInputDialog.getText(self, '修改','请再次输入新密码：')
						if ok and text!='' and text!=' ' and text!='  ' and text!='   ' and text!='    'and text!='     ':
							self.nnpasswd=str(text)
							print(self.nnpasswd)
						else:
							self.nnpasswd="  "
						if self.nnpasswd == self.npasswd:
							with open('passwd.txt', 'w+') as f:
								f.write(self.nnpasswd)
								f.close()
						else:
							QMessageBox.critical(self,"警告",self.tr("前后密码不一致!"))
					else:
						QMessageBox.critical(self,"警告",self.tr("密码错误!"))
				else:
					QMessageBox.critical(self,"警告",self.tr("密码错误!")) 
                    
	def closeEvent(self, event):
		box = QMessageBox(QMessageBox.Question, self.tr("提示"), self.tr("您确定要退出吗？"), QMessageBox.NoButton, self)
		yr_btn = box.addButton(self.tr("是"), QMessageBox.YesRole)
		box.addButton(self.tr("否"), QMessageBox.NoRole)
		box.exec_()
		if box.clickedButton() == yr_btn:
			event.accept()
		else:
			event.ignore()


if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = Example()
	sys.exit(app.exec_())
	'''
	sys.exit(app.exec_())----消息循环结束之后返回0，接着调用sys.exit(0)退出程序
	app.exec_()--------------消息循环结束之后，进程自然也会结束
	'''	
