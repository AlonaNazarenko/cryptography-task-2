class Strumok:
    def __init__(self, key: bytes, iv:bytes):
        assert len(key) in (32, 64)
        assert len(iv) == 32

        self.key = key
        self.iv = iv
        self.type = 256 if len(key) == 32 else 512

        self.state = [0] * 16

    def _bytes_to_words(self, data):
        return[
            int.from_bytes(data[i: i+8], "little")
            for i in range(0, len(data), 8)
        ]

    def _next(self , init=False):


    def _init_state(self, key, iv):

        K = self._bytes_to_words(key)
        IV = self._bytes_to_words(iv)
        MASK = 0xFFFFFFFFFFFFFFFF #mod 64

        if self.type == 256:
            self.state[15], self.state[14], self.state[13], self.state[12] = (~K[0]) & MASK, K[1], (~K[2]) & MASK, K[3]
            self.state[11], self.state[10], self.state[9], self.state[8] = K[0], (~K[1]) & MASK, K[2], K[3]
            self.state[7], self.state[6], self.state[5], self.state[4] = (~K[0]) & MASK, (~K[1]) & MASK, (K[2] ^ IV[3]) & MASK, K[3]
            self.state[3], self.state[2], self.state[1], self.state[0] = (K[0] ^ IV[2]) & MASK, (K[1] ^ IV[1]) & MASK, K[2], (K[3] ^ IV[0]) & MASK
        else:
            self.state[15], self.state[14], self.state[13], self.state[12] =  K[0], (~K[1]) & MASK, K[2], K[3]
            self.state[11], self.state[10], self.state[9], self.state[8] = (~K[7]) & MASK, K[5], (~K[6]) & MASK, (K[4] ^ IV[3]) & MASK
            self.state[7], self.state[6], self.state[5], self.state[4] = (~K[0]) & MASK, K[1], (K[2] ^ IV[2]) & MASK, K[3]
            self.state[3], self.state[2], self.state[1], self.state[0] = (K[4] ^ IV[1]) & MASK, K[5], K[6], (K[7] ^ IV[0]) & MASK


