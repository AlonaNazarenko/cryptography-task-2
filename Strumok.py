from Strumok_tabels import *


class Strumok:
    def __init__(self, key: bytes, iv:bytes):
        assert len(key) in (32, 64)
        assert len(iv) == 32

        self.key = key
        self.iv = iv
        self.type = 256 if len(key) == 32 else 512
        self.MASK = 0xFFFFFFFFFFFFFFFF

        self.state = [0] * 16
        self.r = [0, 0]

        self._init_state(key, iv)

    def _bytes_to_words(self, data):
        words = [
            int.from_bytes(data[i: i+8], "big")
            for i in range(0, len(data), 8)
        ]
        return words[::-1]
    def _t_transform(self, w):
        return (
            strumok_T0[w & 0xFF] ^
            strumok_T1[(w >> 8) & 0xFF] ^
            strumok_T2[(w >> 16) & 0xFF] ^
            strumok_T3[(w >> 24) & 0xFF] ^
            strumok_T4[(w >> 32) & 0xFF] ^
            strumok_T5[(w >> 40) & 0xFF] ^
            strumok_T6[(w >> 48) & 0xFF] ^
            strumok_T7[(w >> 56) & 0xFF]
        )

    def _fsm(self, x, y, z):
        return ((x + y) & self.MASK) ^ z

    def _alpha(self, w):
        return ((w << 8)& self.MASK) ^ strumok_alpha_mul[(w >> 56) & 0xFF ]

    def _alpha_inv(self, w):
        return ((w >> 8)& self.MASK) ^ strumok_alphainv_mul[w & 0xFF]

    def _next(self , init=False):
        r_old = self.r.copy()
        s_old = self.state.copy()

        self.r[1] = self._t_transform(r_old[0])
        self.r[0] = (r_old[1] + s_old[13]) & self.MASK

        for j in range(15):
            self.state[j] = s_old[j + 1]

        self.state[15] = self._alpha(s_old[0]) ^ self._alpha_inv(s_old[11]) ^ s_old[13]
        if init:
            self.state[15] ^= self._fsm(s_old[15], r_old[0], r_old[1])

    def _init_state(self, key, iv):

        K = self._bytes_to_words(key)
        IV = self._bytes_to_words(iv)
        self.MASK = 0xFFFFFFFFFFFFFFFF  # mod 64

        if self.type == 256:
            self.state[15], self.state[14], self.state[13], self.state[12] = (~K[0]) & self.MASK, K[1], (~K[2]) & self.MASK, K[3]
            self.state[11], self.state[10], self.state[9], self.state[8] = K[0], (~K[1]) & self.MASK, K[2], K[3]
            self.state[7], self.state[6], self.state[5], self.state[4] = (~K[0]) & self.MASK, (~K[1]) & self.MASK, (K[2] ^ IV[3]) & self.MASK, K[3]
            self.state[3], self.state[2], self.state[1], self.state[0] = (K[0] ^ IV[2]) & self.MASK, (K[1] ^ IV[1]) & self.MASK, K[2], (K[3] ^ IV[0]) & self.MASK
        else:
            self.state[15], self.state[14], self.state[13], self.state[12] = K[0], (~K[1]) & self.MASK, K[2], K[3]
            self.state[11], self.state[10], self.state[9], self.state[8] = (~K[7]) & self.MASK, K[5], (~K[6]) & self.MASK, (K[4] ^ IV[3]) & self.MASK
            self.state[7], self.state[6], self.state[5], self.state[4] = (~K[0]) & self.MASK, K[1], (K[2] ^ IV[2]) & self.MASK, K[3]
            self.state[3], self.state[2], self.state[1], self.state[0] = (K[4] ^ IV[1]) & self.MASK, K[5], K[6], (K[7] ^ IV[0]) & self.MASK

        for i in range(32):
            self._next(init=True)

        self._next()


    def strum(self):
        res = self._fsm(self.state[15], self.r[0], self.r[1]) ^ self.state[0]
        self._next()
        return res
