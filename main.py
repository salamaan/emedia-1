import sys
from PNG import *

filename = "../images/" + sys.argv[1] + ".png"
png = Png(filename)

png.read_chunks()
png.print_chunks()
png.fourier_and_inverse(filename)
png.create_clean_copy("../new.png")
png.plot_clean_image(filename, "../new.png")
