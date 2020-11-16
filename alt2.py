import win32api
import win32process

pid = 2736

PROCESS_ALL_ACCESS = 0x1F0FFF
processHandle = win32api.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
modules = win32process.EnumProcessModules(processHandle)
processHandle.close()
print (modules)
print (len(modules))



