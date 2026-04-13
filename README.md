# Практичне завдання 2

# Альона Назаренко Єлизавета Загорулько 

## Залежності

pip install python-sat
git clone https://github.com/hadipourh/autoguess

## Запуск

python3 Generate_strumok.py   # генерує файл рівнянь
cd autoguess
python3 autoguess.py --inputfile ../relationfile_strumok512_11clk_mg7_ms9.txt \
  --solver sat --sats minisat22 --maxguess 7 --maxsteps 20 --nograph
cd ..
python3 Simulate_attack.py    # верифікація атаки
python3 Additional.py         # додаткове завдання

![cat](pictures/cat-9125207_1280-1252279691.jpg)
