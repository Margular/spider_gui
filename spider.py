#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from tkinter import *
from tkinter import filedialog
import urllib.request
import urllib.error
import os
import http.client
import time
import re
import random
import _thread
import pickle

class Spider(Frame):
    def __init__(self,master):
        self.headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36'}
        self.enctype = 'utf-8'
        self.proxies = []
        self.initialdir = os.getcwd()
        self.var = dict()   #初始默认值字典

        Frame.__init__(self,master)

        #抓取地址----------------------------------------------------------------------------
        self.frmURL = Frame(master)     #抓取地址框架
        
        self.lblURL = Label(self.frmURL,text='抓取地址:')  #抓取地址标签
        self.lblURL.grid(row=0,column=0,padx=10,sticky=N+W)

        var = StringVar()
        var.set(r'http://www.example.com?id=')
        self.var['url1'] = var
        self.entURL1 = Entry(self.frmURL,width=80,textvariable=self.var['url1'])   #地址1输入框
        self.entURL1.grid(row=0,column=1,sticky=N)

        var = StringVar()
        var.set('1')
        self.var['url2'] = var
        self.entURL2 = Entry(self.frmURL,width=6,textvariable=self.var['url2'])   #地址2输入框
        self.entURL2.grid(row=0,column=2,sticky=N)

        var = StringVar()
        var.set('&user=admin')
        self.var['url3'] = var
        self.entURL3 = Entry(self.frmURL,textvariable=self.var['url3'])  #地址3输入框
        self.entURL3.grid(row=0,column=3,sticky=N)
        
        self.lblStep = Label(self.frmURL,text="递增的量:") #递增量标签
        self.lblStep.grid(row=0,column=4,padx=10)

        var = StringVar()
        var.set("1")
        self.var["step"] = var
        self.entStep = Entry(self.frmURL,width=6,textvariable=self.var["step"])  #递增量输入框
        self.entStep.grid(row=0,column=5,sticky=N+E)
        
        self.frmURL.grid(sticky=N+W+E,row=0,column=0,pady=5)
        #-------------------------------------------------------------------------------------
        
        #代理地址--------------------------以及times-------------------------------------------
        self.frmProxy = Frame(master)   #代理框架

        self.lblProxy = Label(self.frmProxy,text="代理地址:")   #代理标签
        self.lblProxy.grid(row=0,column=0,padx=10)

        var = StringVar()
        var.set(r"http://www.proxy.com/")
        self.var["proxyurl"] = var
        self.entProxyURL = Entry(self.frmProxy,width=80,textvariable=self.var["proxyurl"])  #代理地址输入框
        self.entProxyURL.grid(row=0,column=1)

        var = IntVar()
        var.set(1)
        self.var["http"] = var
        self.cbtHttp = Checkbutton(self.frmProxy,text="HTTP",variable = self.var["http"])    #HTTP开关
        self.cbtHttp.grid(row=0,column=2,padx=10)

        var = IntVar()
        var.set(0)
        self.var["https"] = var
        self.cbtHttps = Checkbutton(self.frmProxy,text="HTTPS",variable = self.var["https"])     #HTTPS开关
        self.cbtHttps.grid(row=0,column=3,padx=10)

        self.lblTimes = Label(self.frmProxy,text="最大失败次数:")   #最大失败次数标签
        self.lblTimes.grid(row=0,column=4,padx=10)

        var = StringVar()
        var.set("5")
        self.var["times"] = var
        self.entTimes = Entry(self.frmProxy,textvariable = self.var["times"],width=6)   #最大失败次数
        self.entTimes.grid(row=0,column=5,padx=10)
        
        self.frmProxy.grid(sticky=W+E,row=1,column=0,pady=5)
        #-------------------------------------------------------------------------------------

        #正则表达式区域--------------------------------------------------------------------------
        self.frmre = Frame(master)  #正则表达式框架
        
        self.frmreURL = LabelFrame(self.frmre,text="网页正则表达式",padx=10)     #网页正则表达式
        self.barURL = Scrollbar(self.frmreURL)
        self.barURL.pack(side=RIGHT,fill=Y)
        reurl = r'''请输入能提取到图片链接的正则表达式，如：
<img\s+?src="(http://(?:ww)[^"]+?\.(?:jpg|jpeg|gif))"
更多信息请查看本程序提供的例子...'''
        self.txtURL = Text(self.frmreURL,width=60,height=10,yscrollcommand=self.barURL.set)
        self.txtURL.pack(side=LEFT)
        self.txtURL.insert(END,reurl)
        self.barURL.config(command=self.txtURL.yview)
        self.frmreURL.grid(sticky=W,row=0,column=0,padx=10)

        self.frmreProxy = LabelFrame(self.frmre,text="代理正则表达式",padx=10)     #代理正则表达式
        self.barProxy = Scrollbar(self.frmreProxy)
        self.barProxy.pack(side=RIGHT,fill=Y)
        reproxy = r'''请输入能提取到代理的正则表达式，请在表达式中提供IP、端口、类型、代理地理位置(可选)，如：
<tr\s+?class[^>]*?>\s*?
    <td>.*?</td>\s*?
    <td>(.*)?</td>\s*?
    <td>(.*)?</td>\s*?
    <td>(.*)?</td>\s*?
    <td>.*?</td>\s*?
    <td>(.*)?</td>\s*?
    <td>.*?</td>\s*?
</tr>'''
        self.txtProxy = Text(self.frmreProxy,width=60,height=10,yscrollcommand=self.barProxy.set)
        self.txtProxy.pack()
        self.txtProxy.insert(END,reproxy)
        self.barProxy.config(command=self.txtProxy.yview)
        self.frmreProxy.grid(sticky=E,row=0,column=1,padx=10)
        
        self.frmre.grid(sticky=W+E,row=2,column=0,pady=5)
        #--------------------------------------------------------------------------------------

        #文件路径区域-----------------------------------------------------------------------------
        self.frmPath = Frame(master)    #文件路径框架

        self.lblPath = Label(self.frmPath,text="保存路径:")      #标签
        self.lblPath.pack(side=LEFT,padx=10)

        var = StringVar()
        var.set(r"C:\图片")
        self.var["path"] = var
        self.entPath = Entry(self.frmPath,textvariable=self.var["path"],width=125)    #保存路径
        self.entPath.pack(side=RIGHT,padx=10)
        
        self.frmPath.grid(sticky=W+E,row=3,column=0,pady=5)
        #---------------------------------------------------------------------------------------

        #按钮区域---------------------------------------------------------------------------------
        self.frmButton = Frame(master)  #按钮框架

        self.btnSpide = Button(self.frmButton,text="给 我 爬!!!",command=self.start_spide) #开始爬
        self.btnSpide.grid(row=0,column=0,padx=25,ipadx=60,ipady=5)

        self.btnSaveAs = Button(self.frmButton,text="配 置 另 存 为...",command=self.save_as)    #保存配置
        self.btnSaveAs.grid(row=0,column=1,padx=25,ipadx=60,ipady=5)

        self.btnLoad = Button(self.frmButton,text="读 取 配 置...",command=self.load)  #读取配置
        self.btnLoad.grid(row=0,column=2,padx=25,ipadx=60,ipady=5)

        self.btnExit = Button(self.frmButton,text="退 出",command=quit)    #退出
        self.btnExit.grid(row=0,column=3,padx=25,ipadx=60,ipady=5)

        self.frmButton.grid(sticky=W+E,row=4,column=0,pady=5)
        #----------------------------------------------------------------------------------------

        #文本框-----------------------------------------------------------------------------------
        self.frmInfo = Frame(master)    #信息框架
        
        self.barInfo = Scrollbar(self.frmInfo)
        self.barInfo.grid(row=0,column=1,sticky=N+S)
        
        self.txtInfo = Text(self.frmInfo , height=20 , yscrollcommand=self.barInfo.set,width=135)
        self.txtInfo.grid(row=0,column=0)

        self.barInfo.config(command=self.txtInfo.yview)

        self.frmInfo.grid(sticky=W+E,row=5,column=0,padx=10,pady=5)
        #----------------------------------------------------------------------------------------

    def save_as(self):
        filename = filedialog.asksaveasfilename(defaultextension=".pkl",filetypes=[("Python打包文件",".pkl"),("所有文件",".*")],initialdir=self.initialdir)
        if not os.path.isabs(filename):
            return
        dic = {}
        for each in self.var:
            dic[each] = self.var[each].get()
        with open(filename,'wb') as f:
            pickle.dump([dic,self.txtURL.get("1.0",END),self.txtProxy.get("1.0",END)],f)

    def load(self):
        filename = filedialog.askopenfilename(defaultextension=".pkl" , filetypes=[("Python打包文件" , ".pkl"),("所有文件",".*")] , initialdir=self.initialdir)
        if not os.path.exists(filename):
            return
        with open(filename,'rb') as f:
            data = pickle.load(f)
        for each in self.var:
            self.var[each].set(data[0][each])
        self.txtURL.delete("1.0",END)
        self.txtURL.insert(END,data[1])
        self.txtProxy.delete("1.0",END)
        self.txtProxy.insert(END,data[2])

    def set_state(self,cmd):
        flag = (cmd == 'Enable')
        self.thread_exit_flag = flag

        if flag == True:
            self.btnSpide['text'] = "给 我 爬!!!"
            self.txtInfo.insert(END,"正在停止小爬爬，请稍等，这可能需要一段时间，如果等待时间过长，可以重新打开本程序......\n")
            self.txtInfo.see(END)
        else:
            self.btnSpide['text'] = "别 爬 了!!!"

        self.entURL1['state'] = NORMAL if flag else "readonly"
        self.entURL3['state'] = NORMAL if flag else "readonly"
        self.entStep['state'] = NORMAL if flag else "readonly"
        self.entProxyURL['state'] = NORMAL if flag else "readonly"
        self.entTimes['state'] = NORMAL if flag else "readonly"
        self.entPath['state'] = NORMAL if flag else "readonly"

        self.cbtHttp['state'] = NORMAL if flag else DISABLED
        self.cbtHttps['state'] = NORMAL if flag else DISABLED
        self.btnSaveAs['state'] = NORMAL if flag else DISABLED
        self.btnLoad['state'] = NORMAL if flag else DISABLED
        
        self.txtURL['state'] = NORMAL if flag else DISABLED
        self.txtURL['background'] = 'white' if flag else '#F0F0F0'
        self.txtProxy['state'] = NORMAL if flag else DISABLED
        self.txtProxy['background'] = 'white' if flag else '#F0F0F0'

        
        
    def start_spide(self):
        self.set_state('Disabled' if self.btnSpide['text'] == "给 我 爬!!!" else 'Enable')
        _thread.start_new_thread(self.spide,tuple()) if self.thread_exit_flag == False else None

    def insert_info(self,info):
        self.txtInfo.insert(END,info)
        self.txtInfo.see(END)
        if self.thread_exit_flag == True:
            self.txtInfo.insert(END,'停止小爬爬成功！！！\n')
            self.txtInfo.see(END)
            _thread.exit()

    def spide(self):
        self.insert_info('正在获取代理...\n')
        self.get_proxy() #取得代理
        self.insert_info('获取代理成功...\n')
        print(self.proxies)
        self.download()  #开始下载

    def get_proxy(self):            #从代理页面提取代理IP及端口
        proxy_url = self.var["proxyurl"].get()
        req = urllib.request.Request(proxy_url,None,self.headers)
        response = self.get_result(req)
        html = response.read().decode('utf-8')
        print(html)
        self.proxies = re.compile(self.txtProxy.get("1.0",END),re.VERBOSE).findall(html)
        #定位协议、IP、端口、地理位置下标
        self.protocol = self.ip = self.port = self.location = 0
        if self.proxies:
            for index in range(len(self.proxies[0])):
                if re.match(r'[Hh][Tt][Tt][Pp][Ss]?',self.proxies[0][index]):
                    self.protocol = index
                    continue
                elif re.match(r'.+\..+\..+\..+',self.proxies[0][index]):
                    self.ip = index
                    continue
                elif self.proxies[0][index].isdecimal():
                    self.port = index
                    continue
                else:
                    self.location = index
                    continue
            if len(self.proxies[0]) < 4:
                self.location = -1
            
    def get_result(self,req_or_url,is_retrieve=False,filename = None):         #取得网页页面
        max_error_times = int(self.var["times"].get())
        error_time = 0
        while True:
            try:
                if error_time == max_error_times:
                    self.insert_info('失败次数达%d次......放弃操作\n' % max_error_times)
                    return None
                error_time += 1
                if is_retrieve:
                    return urllib.request.urlretrieve(req_or_url,filename)
                else:
                    return urllib.request.urlopen(req_or_url)
            except urllib.error.URLError as e:
                if hasattr(e,'code'):
                    self.insert_info(str(e.code)+' '+e.reason+'\n')
                    if e.code == 404:
                        return None
                    self.change_proxy()
                    continue
                elif hasattr(e,'reason'):
                    self.insert_info(str(e)+'\n')
                    self.change_proxy()
                    continue
            except (ConnectionResetError,http.client.BadStatusLine) as e:
                self.insert_info(str(e)+'\n')
                self.change_proxy()
                continue
            except TimeoutError as e:
                self.insert_info(str(e)+'\n')
                self.insert_info('服务器长时间无响应，自动切换代理.....\n')
                self.change_proxy()
                continue
            except UnicodeEncodeError as e:
                self.insert_info(str(e)+'\n')
                return None

    def change_proxy(self):     #切换代理
        random.seed()
        while True: #取得符合要求的代理
            proxy = random.choice(self.proxies)
            protocol = proxy[self.protocol]
            if protocol.lower() == 'http' and self.var['http'].get() or\
                protocol.lower() == 'https' and self.var['https'].get():
                    ip = proxy[self.ip]
                    port = proxy[self.port]
                    break
        #随机使用本地端口或者代理端口
        useproxy = random.choice([False,True])
        if useproxy == False:
            proxy_support = urllib.request.ProxyHandler({})
        else:
            proxy_support = urllib.request.ProxyHandler({protocol.lower():ip+':'+port})
        opener = urllib.request.build_opener(proxy_support)
        opener.addheaders = [('User-Agent',self.headers['User-Agent'])]
        urllib.request.install_opener(opener)
        self.insert_info('智能切换代理:\n')
        if useproxy == False:
            self.insert_info('本机\n')
        else:
            if self.location != -1:
                self.insert_info(proxy[self.location]+'->')
            self.insert_info(protocol+r'://'+ip+':'+port+r'/'+'\n')
        
    def download(self):     #下载图片
        save_path = self.var["path"].get()
        for pic_url in self.get_pic():         
            file_name = os.path.split(pic_url)[1]
            if not os.path.isdir(save_path):    #目录不存在就创建
                os.makedirs(save_path)
            #如果文件已存在则跳过
            if os.path.exists(save_path+'\\'+file_name):
                self.insert_info('文件%s已存在...\n' % file_name)
                continue
            self.get_result(pic_url,True,save_path+'\\'+file_name)
            self.insert_info('本次成功下载第%s页! %s\n' % (self.var['url2'].get() , pic_url))

    def get_pic(self):      #生成器，返回一个图片链接
        while True:
            url = self.var['url1'].get()+self.var['url2'].get()+self.var['url3'].get()
            req = urllib.request.Request(url,None,self.headers)
            response = self.get_result(req)
            if response == None:
                self.insert_info('获取页面失败.....\n')
                self.var['url2'].set(str(int(self.var['url2'].get())+int(self.var['step'].get())))
                continue
            html = response.read().decode(self.enctype)
            pic = re.compile(self.txtURL.get("1.0",END),re.VERBOSE)
            for pic in pic.finditer(html):
                yield pic.group(1)
            time.sleep(5)
            self.var['url2'].set(str(int(self.var['url2'].get())+int(self.var['step'].get())))

def main():
    root = Tk()
    root.title("GUI爬虫-----Margular")
    # Linux不支持ico
    try:
        root.iconbitmap("images" + os.path.sep +"spider.ico")
    except:
        pass
    root.resizable(True , True)
    spider = Spider(root)
    spider.mainloop()
                    
if __name__ == '__main__':
    main()
