from chunks import *
import cv2
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import image


class Png:
    def __init__(self, file_name):
        try:
            self.file = open(file_name, 'rb')
        except IOError as e:
            raise e

        self.PNG_MAGIC_NUMBER = b'\x89PNG\r\n\x1a\n'
        if self.file.read(8) != self.PNG_MAGIC_NUMBER:
            raise Exception('This file is not a PNG')
        self.chunks = []

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

    def print_chunks(self):
        for chunk in self.chunks:
            chunk.__str__()

    def plot_clean_image(self, input_image_filename, clean_image_filename):
        input_img = image.imread(input_image_filename)
        clean_img = image.imread(clean_image_filename)

        f1 = plt.figure(3)

        plt.subplot(121), plt.imshow(input_img)
        plt.title('Input Image'), plt.xticks([]), plt.yticks([])

        plt.subplot(122), plt.imshow(clean_img)
        plt.title('Image after anonymization'), plt.xticks([]), plt.yticks([])

        plt.show()

    def fourier_and_inverse(self, filename):
        img = cv2.imread(filename, 0)
        fourier = np.fft.fft2(img)
        fourier_shifted = np.fft.fftshift(fourier)
        fourier_inverted = np.fft.ifft2(fourier)
        fourier_mag = np.asarray(20 * np.log10(np.abs(fourier_shifted)), dtype=np.uint8)
        fourier_phase = np.asarray(np.angle(fourier_shifted), dtype=np.uint8)

        f1 = plt.figure(1)

        plt.subplot(141), plt.imshow(img, cmap='gray')
        plt.title('Input Image'), plt.xticks([]), plt.yticks([])

        plt.subplot(142), plt.imshow(np.asarray(fourier_inverted, dtype=np.uint8), cmap='gray')
        plt.title('Inverted Image'), plt.xticks([]), plt.yticks([])

        plt.subplot(143), plt.imshow(fourier_mag, cmap='gray')
        plt.title('FFT Magnitude'), plt.xticks([]), plt.yticks([])

        plt.subplot(144), plt.imshow(fourier_phase, cmap='gray')
        plt.title('FFT Phase'), plt.xticks([]), plt.yticks([])

        plt.show()

    def get_chunk_by_type(self, type_):
        try:
            return [chunk for chunk in self.chunks if chunk.type_ == type_][0]
        except IndexError:
            return None

    def create_clean_copy(self, new_file_name):
        def get_ancilary_chunks():
            ancilary_chunks = [
                b'IHDR',
                b'IDAT',
                b'IEND'
            ]
            if self.get_chunk_by_type(b'IHDR').color_type == 3:
                ancilary_chunks.insert(1, b'PLTE')
            return ancilary_chunks

        ancilary_chunks = get_ancilary_chunks()
        file_handler = open(new_file_name, 'wb')
        file_handler.write(self.PNG_MAGIC_NUMBER)

        for chunk in self.chunks:
            if chunk.type_ in ancilary_chunks:
                file_handler.write(chunk.length)
                file_handler.write(chunk.type_)
                file_handler.write(chunk.data)
                file_handler.write(chunk.crc)

        file_handler.close()
