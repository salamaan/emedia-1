from random import getrandbits
import Crypto.Util.number


class Keys:

    def __init__(self, key_size):
        self.key_size = key_size
        self.n = 0
        self.e = 0
        while self.n.bit_length() < key_size * 2:
            self.p = Crypto.Util.number.getPrime(key_size)
            self.q = Crypto.Util.number.getPrime(key_size)
            self.euler = (self.p - 1) * (self.q - 1)
            self.n = self.p * self.q

    def euklides(self, a, b):
        while b:
            a, b = b, a % b

        return a

    def inverse_euklides(self, a, m):
        tmp_m = m
        y = 0
        x = 1
        if (m == 1):
            return 0

        while (a > 1):
            q = a // m
            t = m

            m = a % m
            a = t
            t = y

            y = x - q * y
            x = t

        if (x < 0):
            x = x + tmp_m

        return x

    def generate_public_key(self):
        while True:
            self.e = getrandbits(self.key_size)
            if self.euklides(self.e, self.euler) == 1:
                break

        if 1 > self.e or self.e > self.n:
            self.generate_public_key()
        if self.e % 2 == 0:
            self.generate_public_key()

        public_key = {"e": self.e, "n": self.n}
        return public_key

    def generate_private_key(self):
        self.d = self.inverse_euklides(self.e, self.euler)

        private_key = {"d": self.d, "n": self.n}
        return private_key
