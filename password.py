#!/usr/bin/env python3
# -*- coding: utf-8 -*-
def passwd():
    count = 0    #计数器
    username = "aaa"  #登录用户名
    userpassword = "asd"   #登录密码
        #读取用户名单
    user = open("user.txt","r")
    user_list = user.readlines()
    user.close()
    usern= []
    #读取黑名单用户
    f = open("blacklist.txt","r")
    file_list = f.readlines()
    f.close()
    lock= []
    name = input("登录用户名：")
    #判断用户是否存在
    for i in user_list:
        line = i.strip("\n")
        usern.append(line)
    #判断用户是否在黑名单
    for i in file_list:
        line = i.strip("\n")
        lock.append(line)
    if name in lock:
        print("你的账户已锁定，请联系管理员。")
        return 0
    else:
    #如果用户没有在黑名单，判断用户是否存在
        if name in usern:
            if name == username:
            #如果密码连续输错了三次，锁定账号
                while count <3:
                    password = input("登录密码：")
                    if name == username and password == userpassword:
                        print("欢迎%s!"%name)
                        break
                    else:
                        print("账号和密码不匹配")
                        count +=1
                else:
                    print("对不起，您的账号连续输错三次密码已被锁定，请联系管理员。")
                    f = open("blacklist.txt","w+")
                    li = ['%s'%username]
                    f.writelines(li)
                    f.close()
        else:
            print("用户名不存在，请输入正确的用户名。")