# 主体代码是网上扒的,主要是想要系统托盘那部分代码,这代码我现在也不是很懂……具体出处我也忘了，网上好多雷同的,就随便放一个吧https://bbs.csdn.net/topics/392723265
import os,win32con,win32gui_struct,win32gui,sqlite3,keyboard,threading
import tkinter as tk

__author__ = 'kdxcxs'
__version__ = '0.0.1'

Main = None
icon = 'D:\\Codes\\pyTyper\\kdxcxs.ico'

def getListData(action):
    db_connection = sqlite3.connect('D:\\Codes\\pyTyper\\pyTyper.db')
    root_cursor = db_connection.cursor()
    listTitles = list(root_cursor.execute('SELECT title FROM itemList;'))
    titleMenu = []
    for title in listTitles:
        titleMenu.append((title[0], None, action))
    db_connection.close()
    return titleMenu

def getValue(title):
    db_connection = sqlite3.connect('D:\\Codes\\pyTyper\\pyTyper.db')
    root_cursor = db_connection.cursor()
    value = list(root_cursor.execute('SELECT value FROM itemList WHERE title="{title}";'.format(title=title.replace('\"','\\\"'))))[0][0]
    db_connection.close()
    return value

def pyTyper_type():
    threading.Thread(target=keyboard.write(Main.sysTrayIcon.typerNowValue)).start()

def listenKeyboardEvent():
    keyboard.add_hotkey('ctrl+alt+x',pyTyper_type)

class SysTrayIcon(object):
    QUIT = 'QUIT'
    SPECIAL_ACTIONS = [QUIT]
    FIRST_ID = 2859
    # FIRST_ID = 1314
    def __init__(s,
                 icon,
                 hover_text,
                 menu_options,
                 on_quit=None,
                 default_menu_index=None,
                 window_class_name=None,
                 root=None): # 自己加的,就是下面那一个_Main类,因为后面_add_ids_to_menu_options要调用_Main的changeTyperValue
        s.icon = icon
        s.hover_text = hover_text
        s.on_quit = on_quit
        s.typerTitleID = {}  # typer项目与其id字典
        s.typerNowValue = '' # typer当前触发快捷键输入的值
        s.root = root        # 详见__init__注释

        menu_options = menu_options + (('退出', None, s.QUIT),) # option_text, option_icon, option_action
        s._next_action_id = s.FIRST_ID
        s.menu_actions_by_id = set()
        s.menu_options = s._add_ids_to_menu_options(tuple(menu_options))
        s.menu_actions_by_id = dict(s.menu_actions_by_id)
        del s._next_action_id

        s.default_menu_index = (default_menu_index or 0)
        s.window_class_name = window_class_name or "SysTrayIconPy"

        message_map = {win32gui.RegisterWindowMessage("TaskbarCreated"): s.refresh_icon,
                       win32con.WM_DESTROY: s.destroy,
                       win32con.WM_COMMAND: s.command,
                       win32con.WM_USER+20 : s.notify,}
        # 注册窗口类。
        window_class = win32gui.WNDCLASS()
        window_class.hInstance = win32gui.GetModuleHandle(None)
        window_class.lpszClassName = s.window_class_name
        window_class.style = win32con.CS_VREDRAW | win32con.CS_HREDRAW;
        window_class.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
        window_class.hbrBackground = win32con.COLOR_WINDOW
        window_class.lpfnWndProc = message_map #也可以指定wndproc.
        s.classAtom = win32gui.RegisterClass(window_class)

    def show_icon(s):
        # 创建窗口。
        hinst = win32gui.GetModuleHandle(None)
        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
        s.hwnd = win32gui.CreateWindow(s.classAtom,
                                          s.window_class_name,
                                          style,
                                          0,
                                          0,
                                          win32con.CW_USEDEFAULT,
                                          win32con.CW_USEDEFAULT,
                                          0,
                                          0,
                                          hinst,
                                          None)
        win32gui.UpdateWindow(s.hwnd)
        s.notify_id = None
        s.refresh_icon()
        win32gui.PumpMessages()

    def show_menu(s):
        menu = win32gui.CreatePopupMenu()
        s.create_menu(menu, s.menu_options)
        #win32gui.SetMenuDefaultItem(menu, 1000, 0)

        pos = win32gui.GetCursorPos()
        # See http://msdn.microsoft.com/library/default.asp?url=/library/en-us/winui/menus_0hdi.asp
        win32gui.SetForegroundWindow(s.hwnd)
        win32gui.TrackPopupMenu(menu,
                                win32con.TPM_LEFTALIGN,
                                pos[0],
                                pos[1],
                                0,
                                s.hwnd,
                                None)
        win32gui.PostMessage(s.hwnd, win32con.WM_NULL, 0, 0)

    def destroy(s, hwnd, msg, wparam, lparam):
        if s.on_quit: s.on_quit(s) #运行传递的on_quit
        nid = (s.hwnd, 0)
        win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, nid)
        win32gui.PostQuitMessage(0) # 退出托盘图标

    def notify(s, hwnd, msg, wparam, lparam):
        if lparam == win32con.WM_LBUTTONDBLCLK: # 双击左键
            pass #s.execute_menu_option(s.default_menu_index + s.FIRST_ID)
        elif lparam == win32con.WM_RBUTTONUP: # 单击右键
            s.show_menu()
        elif lparam == win32con.WM_LBUTTONUP: # 单击左键
            s.show_menu()
        return True
        """ 可能的鼠标事件：
        WM_MOUSEMOVE
        WM_LBUTTONDOWN
        WM_LBUTTONUP
        WM_LBUTTONDBLCLK
        WM_RBUTTONDOWN
        WM_RBUTTONUP
        WM_RBUTTONDBLCLK
        WM_MBUTTONDOWN
        WM_MBUTTONUP
        WM_MBUTTONDBLCLK"""

    def _add_ids_to_menu_options(s, menu_options):
        result = []
        # 检测是否是嵌套调用的插入二级菜单,清空原数据方便后面更新字典
        if type(menu_options) == type(['talk','is','cheap']):
            s.typerTitleID = {} # 清空原数据
            if not s.typerNowValue: # 第一次运行,初始化typerNowValue为第一个项目的值
                s.root.changeTyperValue(menu_options[0][0],getValue(menu_options[0][0]))
        for menu_option in menu_options:
            option_text, option_icon, option_action = menu_option
            # 记录每个typer项目的id以便启动时从数据库取value
            if type(menu_options) == type(['talk','is','cheap']):
                s.typerTitleID[s._next_action_id] = option_text
            if callable(option_action) or option_action in s.SPECIAL_ACTIONS:
                s.menu_actions_by_id.add((s._next_action_id, option_action))
                result.append(menu_option + (s._next_action_id,))
            else:
                result.append((option_text,
                               option_icon,
                               s._add_ids_to_menu_options(option_action),
                               s._next_action_id))
            s._next_action_id += 1
        return result

    def refresh_icon(s, **data):
        hinst = win32gui.GetModuleHandle(None)
        if os.path.isfile(s.icon): # 尝试找到自定义图标
            icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
            hicon = win32gui.LoadImage(hinst,
                                       s.icon,
                                       win32con.IMAGE_ICON,
                                       0,
                                       0,
                                       icon_flags)
        else: # 找不到图标文件 - 使用默认值
            hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)

        if s.notify_id: message = win32gui.NIM_MODIFY
        else: message = win32gui.NIM_ADD
        s.notify_id = (s.hwnd,
                          0,
                          win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP,
                          win32con.WM_USER+20,
                          hicon,
                          s.hover_text)
        win32gui.Shell_NotifyIcon(message, s.notify_id)

    def create_menu(s, menu, menu_options):
        for option_text, option_icon, option_action, option_id in menu_options[::-1]:
            if option_icon:
                option_icon = s.prep_menu_icon(option_icon)

            if option_id in s.menu_actions_by_id:                
                item, extras = win32gui_struct.PackMENUITEMINFO(text=option_text,
                                                                hbmpItem=option_icon,
                                                                wID=option_id)
                win32gui.InsertMenuItem(menu, 0, 1, item)
            else:
                submenu = win32gui.CreatePopupMenu()
                s.create_menu(submenu, option_action)
                item, extras = win32gui_struct.PackMENUITEMINFO(text=option_text,
                                                                hbmpItem=option_icon,
                                                                hSubMenu=submenu)
                win32gui.InsertMenuItem(menu, 0, 1, item)

    def prep_menu_icon(s, icon):
        # 首先加载图标。
        ico_x = win32api.GetSystemMetrics(win32con.SM_CXSMICON)
        ico_y = win32api.GetSystemMetrics(win32con.SM_CYSMICON)
        hicon = win32gui.LoadImage(0, icon, win32con.IMAGE_ICON, ico_x, ico_y, win32con.LR_LOADFROMFILE)

        hdcBitmap = win32gui.CreateCompatibleDC(0)
        hdcScreen = win32gui.GetDC(0)
        hbm = win32gui.CreateCompatibleBitmap(hdcScreen, ico_x, ico_y)
        hbmOld = win32gui.SelectObject(hdcBitmap, hbm)
        # 填满背景。
        brush = win32gui.GetSysColorBrush(win32con.COLOR_MENU)
        win32gui.FillRect(hdcBitmap, (0, 0, 16, 16), brush)
        # "GetSysColorBrush返回缓存的画笔而不是分配新的画笔。"
        #  - 暗示没有DeleteObject
        # 画出图标
        win32gui.DrawIconEx(hdcBitmap, 0, 0, hicon, ico_x, ico_y, 0, 0, win32con.DI_NORMAL)
        win32gui.SelectObject(hdcBitmap, hbmOld)
        win32gui.DeleteDC(hdcBitmap)
        return hbm

    def command(s, hwnd, msg, wparam, lparam):
        id = win32gui.LOWORD(wparam)
        s.execute_menu_option(id)

    def execute_menu_option(s, id):
        menu_action = s.menu_actions_by_id[id]
        if menu_action == s.QUIT:
            win32gui.DestroyWindow(s.hwnd)
        elif id in s.typerTitleID:
            menu_action(s.typerTitleID[id],getValue(s.typerTitleID[id]))
            # menu_action(s)
        else:
            menu_action()

class _Main:
    def __init__(s):
        hover_text = "pyTyper" #悬浮于图标上方时的提示
        s.sysTrayIcon = SysTrayIcon(icon, hover_text, (('更新数据', None, s.updateMenu),('关于', None, s.showAbout),), on_quit = s.exit, default_menu_index = 1,root=s) # 先初始化一次,否则下面update会报错未定义
        s.updateMenu()

    def main(s):
        s.sysTrayIcon.show_icon()

    def changeTyperValue(s,title,newValue):
        if s.sysTrayIcon.typerNowValue:
            s.sysTrayIcon.typerNowValue = newValue
            s.sysTrayIcon.hover_text    = 'pyTyper|'+title
            s.sysTrayIcon.refresh_icon()
        else:
            s.sysTrayIcon.typerNowValue = newValue
            s.sysTrayIcon.hover_text    = 'pyTyper|'+title

    def updateMenu(s,new_menu_options=None):
        if not new_menu_options:
            new_menu_options = (('切换', None, getListData(s.changeTyperValue)),('更新数据', None, s.updateMenu),('关于', None, s.showAbout))
        s.sysTrayIcon.menu_options = new_menu_options + (('退出', None, s.sysTrayIcon.QUIT),) # option_text, option_icon, option_action
        s.sysTrayIcon._next_action_id = s.sysTrayIcon.FIRST_ID
        s.sysTrayIcon.menu_actions_by_id = set()
        s.sysTrayIcon.menu_options = s.sysTrayIcon._add_ids_to_menu_options(s.sysTrayIcon.menu_options)
        s.sysTrayIcon.menu_actions_by_id = dict(s.sysTrayIcon.menu_actions_by_id)

    def showAbout(s):
        aboutWindow = tk.Tk()
        aboutWindow.geometry('300x150')
        aboutWindow.iconbitmap(icon)
        aboutTitle  = tk.Label(aboutWindow,text='pyTyper',font=('Harlow Solid Italic', 36))
        aboutTitle.pack()
        aboutWindow.mainloop()

    def exit(s, _sysTrayIcon = None):
        win32gui.PostQuitMessage(0)

if __name__ == '__main__':
    listenKeyboardEvent()
    Main = _Main()
    Main.main()