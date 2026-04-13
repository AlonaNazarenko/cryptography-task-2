import os

def s(t, i):
    """Ім'я змінної LFSR: S_{t*16 + i}"""
    return f"S_{t * 16 + i}"

def r1(t):
    return f"R1_{t}"

def r2(t):
    return f"R2_{t}"

def z(t):
    return f"Z_{t}"


def generate_strumok512(T=11, output_dir="."):
    cipher_name = "strumok512"

    recommended_mg = 7
    recommended_ms = 9

    eqs = f"# Strumok-512, {T} clocks\n"
    eqs += "connection relations\n"

    for t in range(T):
        eqs += f"{z(t)}, {s(t, 15)}, {r1(t)}, {r2(t)}, {s(t, 0)}\n"
        eqs += f"{r2(t + 1)}, {r1(t)}\n"
        eqs += f"{r1(t + 1)}, {r2(t)}, {s(t, 13)}\n"

        for j in range(15):
            eqs += f"{s(t + 1, j)}, {s(t, j + 1)}\n"
        eqs += f"{s(t + 1, 15)}, {s(t, 0)}, {s(t, 11)}, {s(t, 13)}\n"

    eqs += "known\n"
    for t in range(T):
        eqs += f"{z(t)}\n"
    eqs += "target\n" 
    for i in range(16):
        eqs += f"S_{i}\n"
    eqs += "R1_0\nR2_0\n" 
    eqs += "end"

    filename = f"relationfile_{cipher_name}_{T}clk_mg{recommended_mg}_ms{recommended_ms}.txt"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w") as f:
        f.write(eqs)

    print(f" Створено: {filepath}")

    lines = [l for l in eqs.split("\n")
             if l and not l.startswith("#") and l not in ("connection relations", "known", "end")
             and not l.startswith("Z_")]
    print(f"  Кількість рівнянь зв'язку: {len(lines)}")
    print(f"  Тактів: {T}")
    print(f"  Рекомендований розмір базису: {recommended_mg} слів × 64 біт = {recommended_mg * 64} біт")

    return filepath, filename


def main():
    print("Генератор зв'язків Струмок-512 для Autoguess \n")

    fp, fn = generate_strumok512(T=11, output_dir=".")
    print()

    for T in [5, 9, 10, 12, 13]:
        generate_strumok512(T=T, output_dir=".")

if __name__ == "__main__":
    main()