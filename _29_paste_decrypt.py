from _24_cryptor import decrypt

with open('paste_download.txt', 'rb') as f:
    contents = f.read()

with open('paste_download_decrypt.pdf', 'wb') as f:
    f.write(decrypt(contents))
