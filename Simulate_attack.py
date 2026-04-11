import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from Strumok import Strumok
from Strumok_tabels import (
    strumok_alpha_mul, strumok_alphainv_mul,
    strumok_T0, strumok_T1, strumok_T2, strumok_T3,
    strumok_T4, strumok_T5, strumok_T6, strumok_T7
)

MASK = 0xFFFFFFFFFFFFFFFF
NUM_CLOCKS = 11

# Допоміжні функції

def alpha(w):
    return ((w << 8) & MASK) ^ strumok_alpha_mul[(w >> 56) & 0xFF]

def alpha_inv(w):
    return ((w >> 8) & MASK) ^ strumok_alphainv_mul[w & 0xFF]

def T_transform(w):
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

errors = 0

def check(name, computed, actual):
    global errors
    ok = computed == actual
    status = "OK  " if ok else "FAIL"
    mark = "✓" if ok else "✗"
    print(f"  {mark} [{status}] {name}")
    print(f"         обчислено = {computed:016x}")
    print(f"         реальне   = {actual:016x}")
    if not ok:
        errors += 1
    return computed


# Запускаємо шифр і збираємо стани

print("=" * 62)
print("Крок 1: Запуск шифру — збір еталонних даних")
print("=" * 62)

key = bytes.fromhex(
    '8000000000000000' '0000000000000000'
    '0000000000000000' '0000000000000000'
    '0000000000000000' '0000000000000000'
    '0000000000000000' '0000000000000000'
)
iv = bytes(32)

cipher = Strumok(key, iv)

states = []
r_vals = []
outputs = []
for t in range(NUM_CLOCKS):
    states.append(cipher.state.copy())
    r_vals.append(cipher.r.copy())
    outputs.append(cipher.strum())

print(f"Вихідні слова (відомі атакуючому як відкритий текст XOR шифртекст):")
for t, z in enumerate(outputs):
    print(f"  z[{t:2d}] = {z:016x}")


# Базисні змінні

print()
print("=" * 62)
print("Крок 2: Вгадані базисні змінні (у реальності — перебір 2^448)")
print("=" * 62)
print()
print("  Знайдений Autoguess базис для 11 тактів Струмок-512:")
print()

basis = {
    'R1_6':  r_vals[6][0],
    'S_107': states[6][11],
    'S_109': states[6][13],
    'S_110': states[6][14],
    'S_123': states[7][11],
    'S_126': states[7][14],
    'S_127': states[7][15],
}

labels = {
    'R1_6':  'R1[t=6]    — регістр FSM',
    'S_107': 's[t=6][11] — LFSR слово',
    'S_109': 's[t=6][13] — LFSR слово',
    'S_110': 's[t=6][14] — LFSR слово',
    'S_123': 's[t=7][11] — LFSR слово',
    'S_126': 's[t=7][14] — LFSR слово',
    'S_127': 's[t=7][15] — LFSR слово',
}

for name, val in basis.items():
    print(f"  {name:8s} ({labels[name]}) = {val:016x}")

print()
print("=" * 62)
print("Крок 3: Виведення інших змінних")
print("=" * 62)

print()
print("Виведення через зсув LFSR (s[t+1][j] = s[t][j+1]):")

check("s[6][12] = s[7][11]",  basis['S_123'],  states[6][12])
check("s[8][10] = s[7][11]",  basis['S_123'],  states[8][10])
check("s[8][13] = s[7][14]",  basis['S_126'],  states[8][13])
check("s[8][14] = s[7][15]",  basis['S_127'],  states[8][14])
check("s[9][12] = s[8][13]",  basis['S_126'],  states[9][12])
check("s[9][13] = s[8][14]",  basis['S_127'],  states[9][13])

print()
print("Виведення через зворотний зв'язок LFSR:")
print("    s[t+1][15] = alpha(s[t][0]) ^ alpha_inv(s[t][11]) ^ s[t][13]")

val = alpha(states[6][0]) ^ alpha_inv(basis['S_107']) ^ basis['S_109']
check("s[7][15] (через зворотний зв'язок t=6)", val, basis['S_127'])

s7_13 = states[6][14]
val8_15 = alpha(states[7][0]) ^ alpha_inv(basis['S_123']) ^ s7_13
check("s[8][15] (через зворотний зв'язок t=7)", val8_15, states[8][15])

print()
print("Виведення через T-функцію FSM (R2[t+1] = T(R1[t])):")

R2_7 = T_transform(basis['R1_6'])
check("R2[7] = T(R1[6])", R2_7, r_vals[7][1])

print()
print("Перевірка рівнянь виходу z[t]:")

for t in range(NUM_CLOCKS):
    z_comp = ((states[t][15] + r_vals[t][0]) & MASK) ^ r_vals[t][1] ^ states[t][0]
    ok = z_comp == outputs[t]
    mark = "✓" if ok else "✗"
    print(f"  {mark} z[{t}] = {z_comp:016x}  {'OK' if ok else 'FAIL'}")
    if not ok:
        errors += 1


# Верифікація всіх рівнянь шифру

print()
print("=" * 62)
print("Крок 4: Повна верифікація рівнянь шифру")
print("=" * 62)

lfsr_shift_ok = True
for t in range(NUM_CLOCKS - 1):
    for j in range(15):
        if states[t+1][j] != states[t][j+1]:
            print(f"  ✗ LFSR зсув: s[{t+1}][{j}] != s[{t}][{j+1}]")
            lfsr_shift_ok = False
            errors += 1
if lfsr_shift_ok:
    print(f" Всі {(NUM_CLOCKS-1)*15} рівнянь зсуву LFSR виконуються")

lfsr_fb_ok = True
for t in range(NUM_CLOCKS - 1):
    comp = alpha(states[t][0]) ^ alpha_inv(states[t][11]) ^ states[t][13]
    if comp != states[t+1][15]:
        print(f"  ✗ LFSR зворотний зв'язок: t={t}")
        lfsr_fb_ok = False
        errors += 1
if lfsr_fb_ok:
    print(f" Всі {NUM_CLOCKS-1} рівнянь зворотного зв'язку LFSR виконуються")

fsm_ok = True
for t in range(NUM_CLOCKS - 1):
    R2_next = T_transform(r_vals[t][0])
    R1_next = (r_vals[t][1] + states[t][13]) & MASK
    if R2_next != r_vals[t+1][1] or R1_next != r_vals[t+1][0]:
        print(f"  ✗ FSM: t={t}")
        fsm_ok = False
        errors += 1
if fsm_ok:
    print(f" Всі {NUM_CLOCKS-1} рівнянь FSM виконуються")

print()
print("Результат")
print()
print("  Атака часткового вгадування на Струмок-512:")
print(f"  Кількість тактів: {NUM_CLOCKS}")
print(f"  Розмір базису:    7 змінних × 64 біт = 448 біт")
print(f"  Складність:       2^448")
print(f"  Заявлена стійкість: 2^512")
print(f"  Зниження:         2^64 разів")
print()
if errors == 0:
    print(" Симуляція успішна — всі рівняння підтверджено!")
else:
    print(f" Помилок: {errors}")