import random
from Crypto.PublicKey import RSA as rsa
from Crypto.Cipher import PKCS1_OAEP
from cryptography.fernet import Fernet


class RSA:
    def __init__(self, public_key, private_key):
        self.public_key = public_key
        self.private_key = private_key

    def ecb_encrypt(self, data):
        key_size = self.public_key['n'].bit_length()
        block_size = key_size // 8 - 1
        encrypted_data = bytearray()
        padding = bytearray()
        after_iend = bytearray()

        for i in range(0, len(data), block_size):
            bytes_block = bytes(data[i:i + block_size])

            if len(bytes_block) % block_size != 0:
                for empty in range(block_size - (len(bytes_block) % block_size)):
                    padding.append(0)
                bytes_block = padding + bytes_block

            int_block = int.from_bytes(bytes_block, 'big')
            encrypt_block_int = pow(int_block, self.public_key['e'], self.public_key['n'])
            encrypt_block_bytes = encrypt_block_int.to_bytes(block_size + 1, 'big')

            after_iend.append(encrypt_block_bytes[-1])
            encrypt_block_bytes = encrypt_block_bytes[:-1]
            encrypted_data += encrypt_block_bytes

        return encrypted_data, after_iend

    def ecb_decrypt(self, encrypted_data, after_iend):
        key_size = self.private_key['n'].bit_length()
        decrypted_data = bytearray()
        block_size = key_size // 8 - 1
        index = 0

        for i in range(0, len(encrypted_data), block_size):
            encrypted_block_bytes = encrypted_data[i:i + block_size] + after_iend[index].to_bytes(1, 'big')
            encrypted_block_int = int.from_bytes(encrypted_block_bytes, 'big')

            decrypted_block_int = pow(encrypted_block_int, self.private_key['d'], self.private_key['n'])
            decrypted_block_bytes = decrypted_block_int.to_bytes(block_size, 'big')

            decrypted_data += decrypted_block_bytes
            index += 1
        return decrypted_data

    def cbc_encrypt(self, data):
        key_size = self.public_key['n'].bit_length()
        block_size = key_size // 8 - 1
        encrypted_data = bytearray()
        padding = bytearray()
        after_iend = bytearray()
        self.init_vector = random.getrandbits(key_size)
        prev_vector = self.init_vector

        for i in range(0, len(data), block_size):
            bytes_block = bytes(data[i:i + block_size])

            if len(bytes_block) % block_size != 0:
                for empty in range(block_size - (len(bytes_block) % block_size)):
                    padding.append(0)
                bytes_block = padding + bytes_block

            prev_vector = prev_vector.to_bytes(block_size + 1, 'big')
            prev_vector = int.from_bytes(prev_vector[:len(bytes_block)], 'big')

            xor = int.from_bytes(bytes_block, 'big') ^ prev_vector
            encrypt_block_int = pow(xor, self.public_key['e'], self.public_key['n'])
            prev_vector = encrypt_block_int
            encrypt_block_bytes = encrypt_block_int.to_bytes(block_size + 1, 'big')

            after_iend.append(encrypt_block_bytes[-1])
            encrypt_block_bytes = encrypt_block_bytes[:-1]
            encrypted_data += encrypt_block_bytes

        return encrypted_data, after_iend

    def cbc_decrypt(self, encrypted_data, after_iend_data):
        key_size = self.private_key['n'].bit_length()
        decrypted_data = bytearray()
        block_size = key_size // 8 - 1
        prev_vector = self.init_vector
        index = 0

        for i in range(0, len(encrypted_data), block_size):
            encrypted_block_bytes = encrypted_data[i:i + block_size] + after_iend_data[index].to_bytes(1, 'big')
            encrypted_block_int = int.from_bytes(encrypted_block_bytes, 'big')
            decrypted_block_int = pow(encrypted_block_int, self.private_key['d'], self.private_key['n'])

            prev_vector = prev_vector.to_bytes(block_size + 1, 'big')
            prev_vector = int.from_bytes(prev_vector[:block_size], 'big')
            xor = prev_vector ^ decrypted_block_int

            decrypted_block_bytes = xor.to_bytes(block_size, 'big')
            decrypted_data += decrypted_block_bytes

            prev_vector = int.from_bytes(encrypted_block_bytes, 'big')
            index += 1

        return decrypted_data

    def lib_encrypyt(self, filename):
        key = Fernet.generate_key()

        with open('keyfile.key', 'wb') as keyfile:
            keyfile.write(key)

        key = Fernet.generate_key()

        with open('keyfile.key', 'wb') as keyfile:
            keyfile.write(key)

        fernet = Fernet(key)

        with open(filename, 'rb') as original_file:
            original_data = original_file.read()

        encrypted_data = fernet.encrypt(original_data)

        with open("../rsa_images/lib_encrypted.png", 'wb') as encrypted_file:
            encrypted_file.write(encrypted_data)

        fernet = Fernet(key)

        with open("../rsa_images/lib_encrypted.png", 'rb') as encrypted_file:
            encrypted_data = encrypted_file.read()

        decrypted_data = fernet.decrypt(encrypted_data)

        with open("../rsa_images/lib_decrypted.png", 'wb') as decrypted_file:
            decrypted_file.write(decrypted_data)

