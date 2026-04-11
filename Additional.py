import os
import subprocess

def generate_bonus_relations(T=15):
    filename = f"additional_strumok_T{T}.txt"
    
    def s(t, i): return f"S_{t * 16 + i}"
    def r1(t): return f"R1_{t}"
    def r2(t): return f"R2_{t}"
    def z(t): return f"Z_{t}"

    eqs = f"# Additional search: Strumok-512, {T} clocks\n"
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
    eqs += "end"

    with open(filename, "w") as f:
        f.write(eqs)
    return filename

def run_autoguess(filename, max_guess=6):
    print(f"\n Запуск Autoguess для {filename} (шукаємо базис <= {max_guess}) ---")
    
    t_val = filename.split('T')[1].split('.')[0]
    
    cmd = [
        "python3", "autoguess.py",
        "--inputfile", filename,
        "--solver", "sat",
        "--sats", "glucose4",
        "--maxguess", str(max_guess),
        "--maxsteps", t_val,
        "--nograph"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
    except Exception as e:
        print(f"Помилка запуску: {e}")

if __name__ == "__main__":
    bonus_file = generate_bonus_relations(T=15)
    run_autoguess(bonus_file, max_guess=6)