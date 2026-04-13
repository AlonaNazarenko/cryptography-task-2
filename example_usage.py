from Strumok import Strumok

def encrypt(key, iv, plaintext):
    cipher = Strumok(key, iv)
    result = bytearray()
    for i in range(0, len(plaintext), 8):
        block = plaintext[i:i + 8]
        keystream = cipher.strum().to_bytes(8, 'big')
        for j in range(len(block)):
            result.append(block[j] ^ keystream[j])
    return bytes(result)

decrypt = encrypt

iv = bytes(range(32))

print("Режим: 1 - Струмок-256, 2 - Струмок-512")
mode = input("Режим: ")

if mode == "1":
    key = bytes(range(32))
elif mode == "2":
    key = bytes(range(64))
else:
    print("Неправильний режим")
    exit()

message = input("Введіть повідомлення для зашифрування: ").encode()

ciphertext = encrypt(key, iv, message)
print(f"\nCiphertext (hex): {ciphertext.hex()}")

recovered = decrypt(key, iv, ciphertext)
print(f"Decrypted: {recovered.decode()}")