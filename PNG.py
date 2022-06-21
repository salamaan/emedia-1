from chunks import *
import matplotlib.pyplot as plt
from matplotlib import image as mpimg, image
import os
import zlib
from Keys import Keys
from RSA import RSA
from pathlib import Path


class Png:
    PNG_MAGIC_NUMBER = b'\x89PNG\r\n\x1a\n'

    def __init__(self, file_name):
        try:
            self.file = open(file_name, 'rb')
        except IOError as e:
            raise e

        if self.file.read(8) != self.PNG_MAGIC_NUMBER:
            raise Exception('This file is not a PNG')
        self.chunks = []

        self.idat_data = bytearray()

        self.encrypted_data = bytearray()
        self.decrypted_data = bytearray()
        self.after_iend_data = bytearray()

    def __del__(self):
        try:
            self.file.close()
        except AttributeError:
            pass

    def read_chunks(self):
        self.chunks = []
        while True:
            length = self.file.read(Chunk.LENGTH_FIELD_LEN)
            type_ = self.file.read(Chunk.TYPE_FIELD_LEN)
            data = self.file.read(int.from_bytes(length, 'big'))
            crc = self.file.read(Chunk.CRC_FIELD_LEN)

            chunk_class_type = CHUNKTYPES.get(type_, Chunk)
            chunk = chunk_class_type(length, type_, data, crc)
            self.chunks.append(chunk)

            if type_ == b"IEND":
                self.file.seek(8)
                break

    def encode_data(self, algorithm, keys_size, filename):
        data = b''.join(chunk.data for chunk in self.chunks if chunk.type_ == b'IDAT')
        self.idat_data = zlib.decompress(data)

        keys = Keys(keys_size)
        public_key = keys.generate_public_key()
        private_key = keys.generate_private_key()
        rsa = RSA(public_key, private_key)

        rsa.lib_encrypyt(filename)

        if algorithm == "ecb":
            self.encrypted_data, self.after_iend_data = rsa.ecb_encrypt(self.idat_data)
            self.decrypted_data = rsa.ecb_decrypt(self.encrypted_data, self.after_iend_data)

        if algorithm == "cbc":
            self.encrypted_data, self.after_iend_data = rsa.cbc_encrypt(self.idat_data)
            self.decrypted_data = rsa.cbc_decrypt(self.encrypted_data, self.after_iend_data)

    def print_chunks(self):
        for chunk in self.chunks:
            chunk.__str__()

    def create_image(self, image_path, data):
        if Path(image_path).is_file():
            os.remove(image_path)

        tmp_file = open(image_path, 'wb')
        tmp_file.write(Png.PNG_MAGIC_NUMBER)

        for chunk in self.chunks:
            if chunk.type_ in [b'IDAT']:
                new_data = zlib.compress(data, 9)
                new_crc = zlib.crc32(new_data, zlib.crc32(struct.pack('>4s', b'IDAT')))
                chunk_len = len(new_data)
                tmp_file.write(struct.pack('>I', chunk_len))
                tmp_file.write(chunk.type_)
                tmp_file.write(new_data)
                tmp_file.write(struct.pack('>I', new_crc))
            else:
                tmp_file.write(chunk.length)
                tmp_file.write(chunk.type_)
                tmp_file.write(chunk.data)
                tmp_file.write(chunk.crc)

        tmp_file.close()

    def display_image(self, image_path, title):
        file = open(image_path, 'rb')
        file.seek(0)
        img = mpimg.imread(file)
        plt.imshow(img)
        plt.title(title)
        plt.show()

    def display_images(self, path1, path2, path3):
        img1 = image.imread(path1)
        img2 = image.imread(path2)
        img3 = image.imread(path3)

        f1 = plt.figure(1)

        plt.subplot(131), plt.imshow(img1)
        plt.title('Input image'), plt.xticks([]), plt.yticks([])

        plt.subplot(132), plt.imshow(img2)
        plt.title('Decrypted ecb'), plt.xticks([]), plt.yticks([])

        plt.subplot(133), plt.imshow(img3)
        plt.title('Decrypted cbc'), plt.xticks([]), plt.yticks([])

        plt.show()
