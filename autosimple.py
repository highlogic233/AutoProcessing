import winreg
import win32ui
import cv2
import os
import numpy as np
import tkinter as tk
import _thread


def getmargin(frame, bias):
    mgt, mgb, mgl, mgr = 0, 0, 0, 0

    def comp3(x, y):
        for i in temp:
            if comp(frame[x, y], i, bias):
                return False
        temp.append(frame[x, y])
        if len(temp) > 2:
            return True

    frame = np.array(frame)

    marginTop = []
    for x in range(1, int(height / 10)):
        temp = [frame[x, 0]]
        for y in range(0, width):
            if comp3(x, y):
                break
        else:
            marginTop.insert(0, [x, 0])

    for i in marginTop:
        for y in range(0, width):
            if not comp(frame[i[0], y], frame[i[0] + 1, y], bias):
                i[1] += 1
    max = 0
    for i in marginTop:
        if i[1] > max:
            max = i[1]
            mgt = i[0] + 1

    marginBottom = []
    for x in range(2, int(height / 10)):
        temp = [frame[height - x, 0]]
        for y in range(0, width):
            if comp3(height - x, y):
                break
        else:
            marginBottom.insert(0, [height - x, 0])

    for i in marginBottom:
        for y in range(0, width):
            if not comp(frame[i[0], y], frame[i[0] - 1, y], bias):
                i[1] += 1
    max = 0
    for i in marginBottom:
        if i[1] > max:
            max = i[1]
            mgb = height - i[0]

    marginLeft = []
    for y in range(1, int(width / 3)):
        temp = [frame[0, y]]
        for x in range(mgt, height - mgb):
            if comp3(x, y):
                break
        else:
            marginLeft.insert(0, [y, 0])
    for i in marginLeft:
        for x in range(mgt, height - mgb):
            if not comp(frame[x, i[0]], frame[x, i[0] + 1], bias):
                i[1] += 1
    max = 0
    for i in marginLeft:
        if i[1] > max:
            max = i[1]
            mgl = i[0] + 1

    marginRight = []
    for y in range(2, int(width / 3)):
        temp = [frame[0, width - y]]
        for x in range(mgt, height - mgb):
            if comp3(x, width - y):
                break
        else:
            marginRight.insert(0, [width - y, 0])

    for i in marginRight:
        for x in range(mgt, height - mgb):
            if not comp(frame[x, i[0]], frame[x, i[0] - 1], bias):
                i[1] += 1
    max = 0
    for i in marginRight:
        if i[1] > max:
            max = i[1]
            mgr = width - i[0]
    return [mgt, mgb, mgl, mgr]


def comp(a, b, bias):  # 比较a，b是否相似。
    temp = a.astype(np.int32) - b.astype(np.int32)
    if (temp < bias).all() and (temp > -bias).all():
        return 1
    return 0


def judge(img):  # 这个函数输入帧，返回case。
    def comp2(s1, s2):  # 输入坐标，比较RGB值是否相似。
        flag = 1
        for i in range(0, 2):
            if s2 == "w":
                temp = white
            else:
                temp = img[s2[i][1], s2[i][0]]
            if not comp(img[s1[i][1], s1[i][0]], temp, bias):
                flag = 0
        return flag

    pause = 0  # 1代表暂停。
    case = 0  # 0为不剪，1为剪掉，2为加速(不拖干员)，3为加速（正常拖干员），4为加速（暂停拖干员），5为二倍速。
    sort = 3
    sped = 1  # 倍速。
    if comp2(p2, p3):
        pause = 1
    if comp2(p4, "w"):
        sort = 1
        sped = 2
    elif comp2(p1, "w"):
        sort = 1
        sped = 1
    elif comp2(p2, "w"):
        sort = 2
    if (sort == 1):
        if (pause == 1):
            case = 1
        elif sped == 1:
            case = 5
    if (sort == 2):
        if (pause == 0):
            case = 2
        elif (s1 == 0):
            case = 1
    if (sort == 3):
        if (pause == 0):
            case = 3
        else:
            case = 4
    return case


def get_desktop():  # 获取桌面路径。
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
    return winreg.QueryValueEx(key, "Desktop")[0]


def openFile():  # Select a file and return the path.
    dlg = win32ui.CreateFileDialog(1)
    dlg.SetOFNInitialDir(desktop)
    dlg.DoModal()
    return dlg.GetPathName()


def toPic():
    temp = 0
    c = 0
    if not os.path.exists(desktop + '\\temp'):
        os.makedirs(desktop + '\\temp')  # 在桌面创建临时文件夹。

    def saveframe():
        tempPath = desktop + '\\temp\\' + str(c) + '.jpg'  # 这是保存路径。
        cv2.imwrite(tempPath, frame)  # 保存为图片。

    while (1):
        c += 1
        if c > frames_num:
            return 0
        process = round(c / frames_num * 100, 2)  # 计算进度条。
        text2.set('Extracting frames: ' + str(process) + '%')
        ret, frame = capture.read()  # 提取帧。
        if prese(c):
            saveframe()
            continue
        case = judge(frame)
        if case == 1:
            continue
        if case == 0:
            temp = 0
        else:
            temp += 1
        if case == 2:
            if temp % speed1 != 1 and speed1 != 1:  # 每几帧提取一帧，起到加速效果。
                continue
        if case == 3:
            if temp % speed2 != 1 and speed2 != 1:  # 每几帧提取一帧，起到加速效果。
                continue
        if case == 4:
            if temp % speed3 != 1 and speed3 != 1:  # 每几帧提取一帧，起到加速效果。
                continue
        if case == 5:
            if temp % 2 != 1 and s2 == 1:  # 每几帧提取一帧，起到加速效果。
                continue
        saveframe()


def pre():  # 准备工作。
    if startd == 1:
        return
    global desktop, path, p1, p2, p3, p4, frames_num, fps, width, height, capture, pred, preserve1
    desktop = get_desktop()
    path = openFile()  # 打开文件。
    if path == '':
        return
    fpath, fname = os.path.split(path)
    text1.set(fname)
    capture = cv2.VideoCapture(path)
    # 视频信息。
    frames_num = capture.get(7)  # 获取视频总帧数。
    fps = round(capture.get(5))
    width = int(capture.get(3))
    height = int(capture.get(4))
    wid = width - marginLeft - marginRight
    hei = height - marginTop - marginBottom

    if len(preserve) != 0:
        preserve1 = preserve.split(' ')
        for i in range(0, len(preserve1)):
            preserve1[i] = preserve1[i].split('-')
            for j in range(0, 2):
                preserve1[i][j] = round(float(preserve1[i][j]) * fps)
    # 像素点。
    data = [[0.126, 0.074], [0.098, 0.074], [0.112, 0.07], [0.112, 0.081], [0.254, 0.094], [0.254, 0.1], [0.234, 0.095]]
    for i in range(0, 7):
        data[i] = [round(wid - data[i][0] * hei + marginLeft), round(data[i][1] * hei + marginTop)]
    p1 = [data[4], data[5]]
    p2 = [data[0], data[1]]
    p3 = [data[2], data[3]]
    p4 = [data[6], data[6]]
    # 倍速键（1倍速),暂停键,暂停键中间,倍速键（2倍速).
    pred = 1


def trans():
    global startd
    file_dir = desktop + '\\temp\\'
    list = os.listdir(file_dir)
    list.sort(key=lambda fn: os.path.getmtime(file_dir + fn) if not os.path.isdir(file_dir + fn) else 0)
    img = cv2.imread(file_dir + list[2])
    imgInfo = img.shape
    size = (imgInfo[1], imgInfo[0])
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # opencv3.0
    videoWrite = cv2.VideoWriter(desktop + '\\res.mp4', fourcc, fps, size)
    length = len(list)
    cnt = 0
    for i in list:
        fileName = desktop + '\\temp\\' + str(i)
        img = cv2.imread(fileName)
        videoWrite.write(img)  # 写入方法 1 jpg data
        cnt += 1
        process = round(cnt / length * 100, 2)
        text2.set("Generating new video: " + str(process) + "%")
    text2.set('''The video has been saved to the desktop.
    You can delete the temporary folder on your desktop。''')
    startd = 0


def start():
    global startd
    if pred == 1:
        if startd == 1:
            return
        startd = 1

        def temp():
            toPic()
            trans()

        _thread.start_new_thread(temp, ())
    else:
        text2.set("Please select a file first.")


def settings():
    if startd == 1:
        return
    window2 = tk.Tk()
    window2.title('Settings')
    window2.geometry('800x600')
    window2.resizable(0, 0)

    def getmar():
        if pred == 0:
            return
        capture.set(cv2.CAP_PROP_POS_FRAMES, int(frames_num / 2))
        ret, frame = capture.read()
        mar = getmargin(frame, 25)
        en4.delete(0, 'end')
        en5.delete(0, 'end')
        en6.delete(0, 'end')
        en7.delete(0, 'end')
        en4.insert(0, mar[0])
        en5.insert(0, mar[1])
        en6.insert(0, mar[2])
        en7.insert(0, mar[3])
        capture.set(cv2.CAP_PROP_POS_FRAMES, 0)

    def refresh():
        dict.item()['speed1'] = int(en1.get())
        dict.item()['speed2'] = int(en2.get())
        dict.item()['speed3'] = int(en3.get())
        dict.item()['marginTop'] = int(en4.get())
        dict.item()['marginBottom'] = int(en5.get())
        dict.item()['marginLeft'] = int(en6.get())
        dict.item()['marginRight'] = int(en7.get())
        dict.item()['bias'] = int(en8.get())
        dict.item()['s1'] = int(en9.get())
        dict.item()['s2'] = int(en10.get())
        dict.item()['preserve'] = en11.get()
        np.save("setting", dict)
        text2.set('The settings have been saved!')
        window2.destroy()

    la1 = tk.Label(window2, width=18, text='子弹时间 加速倍率', font=(' ', 15))
    la1.place(x=80, y=40, anchor='nw')
    en1 = tk.Entry(window2, width=10)
    en1.place(x=350, y=45, anchor='nw')
    en1.insert(0, dict.item()['speed1'])

    la2 = tk.Label(window2, width=18, text='拖干员 加速倍率', font=(' ', 15))
    la2.place(x=80, y=80, anchor='nw')
    en2 = tk.Entry(window2, width=10)
    en2.place(x=350, y=85, anchor='nw')
    en2.insert(0, dict.item()['speed2'])

    la3 = tk.Label(window2, width=18, text='暂停拖干员 加速倍率', font=(' ', 15))
    la3.place(x=80, y=120, anchor='nw')
    en3 = tk.Entry(window2, width=10)
    en3.place(x=350, y=125, anchor='nw')
    en3.insert(0, dict.item()['speed3'])

    la4 = tk.Label(window2, width=18, text='marginTop', font=(' ', 15))
    la4.place(x=80, y=160, anchor='nw')
    en4 = tk.Entry(window2, width=10)
    en4.place(x=350, y=165, anchor='nw')
    en4.insert(0, dict.item()['marginTop'])

    la5 = tk.Label(window2, width=18, text='marginBottom', font=(' ', 15))
    la5.place(x=80, y=200, anchor='nw')
    en5 = tk.Entry(window2, width=10)
    en5.place(x=350, y=205, anchor='nw')
    en5.insert(0, dict.item()['marginBottom'])

    la6 = tk.Label(window2, width=18, text='marginLeft', font=(' ', 15))
    la6.place(x=80, y=240, anchor='nw')
    en6 = tk.Entry(window2, width=10)
    en6.place(x=350, y=245, anchor='nw')
    en6.insert(0, dict.item()['marginLeft'])

    la7 = tk.Label(window2, width=18, text='marginRight', font=(' ', 15))
    la7.place(x=80, y=280, anchor='nw')
    en7 = tk.Entry(window2, width=10)
    en7.place(x=350, y=285, anchor='nw')
    en7.insert(0, dict.item()['marginRight'])

    la8 = tk.Label(window2, width=18, text='RGB偏差值', font=(' ', 15))
    la8.place(x=80, y=320, anchor='nw')
    en8 = tk.Entry(window2, width=10)
    en8.place(x=350, y=325, anchor='nw')
    en8.insert(0, dict.item()['bias'])

    la9 = tk.Label(window2, width=18, text='保留 暂停开技能', font=(' ', 15))
    la9.place(x=80, y=360, anchor='nw')
    en9 = tk.Entry(window2, width=10)
    en9.place(x=350, y=365, anchor='nw')
    en9.insert(0, dict.item()['s1'])

    la10 = tk.Label(window2, width=18, text='一倍速统一成二倍速', font=(' ', 15))
    la10.place(x=80, y=400, anchor='nw')
    en10 = tk.Entry(window2, width=10)
    en10.place(x=350, y=405, anchor='nw')
    en10.insert(0, dict.item()['s2'])

    la11 = tk.Label(window2, width=18, text='以下时间段不作处理', font=(' ', 15))
    la11.place(x=80, y=440, anchor='nw')
    en11 = tk.Entry(window2, width=40)
    en11.place(x=350, y=445, anchor='nw')
    en11.insert(0, dict.item()['preserve'])

    bu1 = tk.Button(window2, text='Save', font=('Arial', 12), width=20, height=1, command=refresh)
    bu1.place(x=100, y=530, anchor='nw')

    bu2 = tk.Button(window2, text='自动计算边框', font=('Arial', 12), width=20, height=1, command=getmar)
    bu2.place(x=300, y=530, anchor='nw')


def prese(c):
    if len(preserve) == 0:
        return 0
    for i in range(0, len(preserve1)):
        if c > preserve1[i][0] and c < preserve1[i][1]:
            return 1
    return 0


# 以下为代码区。
white = np.array([255, 255, 255])
process = 0  # 进度条。
pred = 0
startd = 0

try:
    dict = np.load("setting.npy", allow_pickle=True)
    speed1 = dict.item()['speed1']
    speed2 = dict.item()['speed2']
    speed3 = dict.item()['speed3']
    marginTop = dict.item()['marginTop']
    marginBottom = dict.item()['marginBottom']
    marginLeft = dict.item()['marginLeft']
    marginRight = dict.item()['marginRight']
    bias = dict.item()['bias']
    s1 = dict.item()['s1']
    s2 = dict.item()['s2']
    preserve = dict.item()['preserve']
except:
    dict = {'speed1': 4, 'speed2': 2, 'speed3': 2, 'marginTop': 0, 'marginBottom': 0,
            'marginLeft': 0, 'marginRight': 0, 'bias': 10, 's1': 1, 's2': 1, 'preserve': '0-5'}
    np.save("setting", dict)

window = tk.Tk()
window.title('PauseSlayer V1.0    By : High-Logic')
window.geometry('800x600')
window.resizable(0, 0)

text1 = tk.StringVar()
la1 = tk.Label(window, bg='#bebebe', textvariable=text1, width=60, font=('Arial', 15))
la1.place(x=80, y=40, anchor='nw')
text1.set('You have not selected a file.')

bu1 = tk.Button(window, text='Select a file', font=('Arial', 12), width=15, height=1, command=pre)
bu1.place(x=80, y=100, anchor='nw')

bu2 = tk.Button(window, text='Start', font=('Arial', 12), width=15, height=1, command=start)
bu2.place(x=240, y=100, anchor='nw')

bu3 = tk.Button(window, text='Settings', font=('Arial', 12), width=15, height=1, command=settings)
bu3.place(x=400, y=100, anchor='nw')

text2 = tk.StringVar()
la2 = tk.Label(window, bg='#bebebe', justify='left', textvariable=text2, width=60, height=4, font=('Arial', 15))
la2.place(x=80, y=170, anchor='nw')
text2.set('''1. Please make sure your computer has enough space.
    (2GB or more is recommended)
2. The beginning will be skipped by default. You can avoid it by settings.''')

window.mainloop()
