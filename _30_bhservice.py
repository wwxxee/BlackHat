import os
import servicemanager  # A module that interfaces with the Windows Service Control Manager.
import shutil
import subprocess
import sys

import win32event
import win32service
import win32serviceutil
"""
win32service子模块提供了对服务管理API的包装.
win32serviceutil是对win32service模块的包装，使用它可以更方便地对服务进行控制。
win32serviceutil.ServiceFramework是封装得很好的Windows服务框架
windows 服务参考：https://www.jianshu.com/p/7f31ecebda28
"""

SOURCE_DIR = 'D:\\test\\tmp'
TARGET_DIR = 'C:\\Windows\\TEMP'


class BHServerService(win32serviceutil.ServiceFramework):
    _svc_name_ = 'BlackHatService'
    _svc_display_name_ = 'Black Hat Service'
    _svc_description_ = ("Execute VBScripts at regular intervals." + "what could possibly go wrong?")

    def __init__(self, args):
        self.vbs = os.path.join(TARGET_DIR, 'bhservice_task.vbs')
        self.timeout = 1000 * 60  # 一分钟超时时间
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        # SERVICE_STOP_PENDING	0x00000003	服务正在停止。
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        # SERVICE_RUNNING	0x00000004	服务正在运行。
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        self.main()

    def main(self):
        while True:
            ret_code = win32event.WaitForSingleObject(self.hWaitStop, self.timeout)
            # WAIT_OBJECT_0  0x00000000L  指定对象的状态已发出信号。
            if ret_code == win32event.WAIT_OBJECT_0:
                servicemanager.LogInfoMsg("Service is stopping")
                break
            src = os.path.join(SOURCE_DIR, 'bhservice_task.vbs')
            shutil.copy(src, self.vbs)
            subprocess.call("cscript.exe %s" % self.vbs, shell=False)
            # subprocess.call('calc.exe')
            os.unlink(self.vbs)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        # Initialize the module for hosting a service. This is generally called automatically
        servicemanager.Initialize()

        # 准备在EXE中承载单个服务，参数为要承载的Python类。
        servicemanager.PrepareToHostSingle(BHServerService)

        # 通过调用win32 StartServiceCtrlDispatcher函数启动服务
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(BHServerService)
