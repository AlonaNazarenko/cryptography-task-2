import time
from Strumok import Strumok

KEY_256 = bytes(range(32))
KEY_512 = bytes(range(64))
IV      = bytes(range(32))

SIZES = [1, 5, 10, 50, 100]

def measure(key, label):
    print(f"\n{label}")
    print(f"{'Обсяг':<12} {'Час (с)':<12} {'Швидкість (МБ/с)'}")
    print("-" * 40)
    max_speed = 0
    for mb in SIZES:
        words = (mb * 1024 * 1024) // 8
        cipher = Strumok(key, IV)
        start = time.perf_counter()
        for _ in range(words):
            cipher.strum()
        elapsed = time.perf_counter() - start
        speed = mb / elapsed
        max_speed = max(max_speed, speed)
        print(f"{mb:<12} {elapsed:<12.3f} {speed:.2f}")
    print(f"Максимальна швидкість: {max_speed:.2f} МБ/с")

measure(KEY_256, "Струмок-256")
measure(KEY_512, "Струмок-512")