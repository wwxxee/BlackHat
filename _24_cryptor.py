from Cryptodome.Cipher import AES, PKCS1_OAEP
from Cryptodome.PublicKey import RSA
from Cryptodome.Random import get_random_bytes
from io import BytesIO

import base64
import zlib

"""
创建一套混合加密流程：AES对称加密算法。加密速度非常快，可以用于处理大量的文本数据。
AES为分组密码，分组密码也就是把明文分成一组一组的，每组长度相等，每次加密一组数据，直到加密完整个明文。
在AES标准规范中，分组长度只能是128位，也就是说，每个分组为16个字节

RSA非对称加密：公钥加密，私钥解密。使用RSA来加密AES算法所使用的密钥。
"""


def generate():
    # 生成2048位密钥对
    new_key = RSA.generate(2048)
    # exportKey 与export_key 等价
    private_key = new_key.exportKey()
    public_key = new_key.publickey().exportKey()

    # 分别写公钥与私钥到文件中
    with open('key.pri', 'wb') as f:
        f.write(private_key)

    with open('key.pub', 'wb') as f:
        f.write(public_key)


def get_rsa_cipher(keytype):
    with open(f'key.{keytype}') as f:
        key = f.read()

    rsakey = RSA.importKey(key)
    # PKCS1_OAEP.new(rsakey)返回一个密码对象。有encryt和decrypt方法用于加解密消息
    # size_in_bytes() RSA密钥的长度
    return (PKCS1_OAEP.new(rsakey), rsakey.size_in_bytes())


def encrypt(text):
    # 压缩字节
    compressed_text = zlib.compress(text)

    # 随机生成一枚会话密钥作为AES的密钥
    sessiong_key = get_random_bytes(16)

    # new方法的key参数It must be 16 (AES-128), 24 (AES-192) or 32 (AES-256) bytes long.
    cipher_aes = AES.new(sessiong_key, AES.MODE_EAX)

    # 对压缩过的明文进行加密
    ciphertext, tag = cipher_aes.encrypt_and_digest(compressed_text)

    # 现在信息已经加密，我们还需要将AES密钥与密文一起附在返回的载荷里传回去
    # 这样接收方才能解密这些内容

    # 用之前RSA生成的公钥对AES会话密钥进行加密
    cipher_rsa, _ = get_rsa_cipher('pub')
    encrypted_session_key = cipher_rsa.encrypt(sessiong_key)

    # 将解密所需要的所有信息(nonce, ciphertext, tag) + 加密后的密钥打包在一段载荷里并且用base64编码返回
    msg_payload = encrypted_session_key + cipher_aes.nonce + tag + ciphertext
    encrypted = base64.encodebytes(msg_payload)

    return encrypted


def decrypt(encrypted):
    encrypted_bytes = BytesIO(base64.decodebytes(encrypted))
    cipher_rsa, keysize_in_bytes = get_rsa_cipher('pri')

    encrypted_session_key = encrypted_bytes.read(keysize_in_bytes)
    nonce = encrypted_bytes.read(16)
    tag = encrypted_bytes.read(16)
    ciphertext = encrypted_bytes.read()

    # 用RSA私钥解密AES密钥
    session_key = cipher_rsa.decrypt(encrypted_session_key)
    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)

    # 解密且验证tag
    decrypted = cipher_aes.decrypt_and_verify(ciphertext, tag)

    plaintext = zlib.decompress(decrypted)

    return plaintext


if __name__ == '__main__':
    # generate()
    plaintext = b'hello world'
    print(decrypt(encrypt(plaintext)))

