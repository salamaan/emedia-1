import sys
import os
from PNG import *

os.system("clear")

key_size = 512
path = "../images/" + sys.argv[1] + ".png"
new_path = "../rsa_images/"

png = Png(path)
png.read_chunks()
png.print_chunks()

png.encode_data("ecb", key_size, path)
png.create_image(new_path + "ecb_encrypted.png", png.encrypted_data)
png.create_image(new_path + "ecb_decrypted.png", png.decrypted_data)

png.encode_data("cbc", key_size, path)
png.create_image(new_path + "cbc_encrypted.png", png.encrypted_data)
png.create_image(new_path + "cbc_decrypted.png", png.decrypted_data)

png.display_images(path, new_path + "ecb_decrypted.png", new_path + "cbc_decrypted.png")




