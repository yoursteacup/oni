import asyncio
import os
import random
import time
from datetime import datetime

WIDTH = 60
HEIGHT = 10
output_lines = []
user_input = ""
input_lock = asyncio.Lock()

# Настраиваемая тема
class Theme:
    def __init__(self):
        self.RESET = "\033[0m"
        self.BORDER_COLOR = "\033[38;5;27m"  # Глубокий темно-синий (аппетитный)
        self.TEXT_COLOR = "\033[92m"    # Зеленый для текста
        self.BOLD = "\033[1m"
        self.DIM = "\033[2m"
        self.RED = "\033[91m"
        self.YELLOW = "\033[93m"
        self.MAGENTA = "\033[95m"
        self.CYAN = "\033[96m"
        self.BACKGROUND = ""  # Пустой - без фона
        self.REVERSE = "\033[7m"
        self.BLINK = "\033[5m"

theme = Theme()

# Глитч-символы
GLITCH_CHARS = "▒▓░█▄▀▌▐╫╪┼╬╋╓╔╕╖╗╘╙╚╛╜╝╞╟╠╡╢╣╤╥╦╧╨╩"
ARTIFACT_CHARS = "◊◈◉○●□■▪▫◘◙◚◛⬚⬛⬜⬝☰☱☲☳☴☵☶☷"
CORRUPT_CHARS = "£¥§¶ßðþΔΩΣπ"
DIGITAL_CHARS = "₀₁₂₃₄₅₆₇₈₉⁰¹²³"

# Глитч-состояние
glitch_active = False
glitch_intensity = 0.0
glitch_type = 'light'
last_glitch_time = 0

def clear():
    print("\033[2J\033[H", end="")

def random_glitch_char(char_type='normal'):
    if char_type == 'corrupt':
        return random.choice(CORRUPT_CHARS)
    elif char_type == 'digital':
        return random.choice(DIGITAL_CHARS)
    else:
        return random.choice(GLITCH_CHARS + ARTIFACT_CHARS)

def apply_glitch_to_string(s, intensity=0.1):
    global glitch_type
    if random.random() > intensity:
        return s
    
    result = list(s)
    # Не трогаем спецсимволы рамки
    box_chars = '╔═╦╗║╚╝'
    
    for i in range(len(result)):
        if result[i] not in box_chars and random.random() < intensity * 0.3:
            if glitch_type == 'corrupt':
                result[i] = random_glitch_char('corrupt')
            elif glitch_type == 'digital':
                result[i] = random_glitch_char('digital')
            else:
                result[i] = random_glitch_char()
    return ''.join(result)

def draw_box(title: str, content: list[str], height: int, width: int):
    global glitch_active, glitch_intensity, glitch_type
    
    # Случайный сдвиг строк при глитче
    h_offset = 0
    if glitch_active and glitch_type == 'shift' and random.random() < glitch_intensity * 0.5:
        h_offset = random.randint(-1, 1)
    
    # Волновой эффект
    wave_offset = 0
    if glitch_active and glitch_type == 'wave':
        wave_offset = int(time.time() * 10 % width / 10)
    
    # Получаем текущее время
    current_time = datetime.now().strftime("%H:%M:%S")
    
    # Вычисляем длину для правильного выравнивания
    title_section = f" {title} "
    time_section = f" {current_time} "
    border_width = width - len(title_section) - len(time_section) - 2
    
    # Верхняя граница с ONI слева и временем справа
    top = f"╔{title_section}{'═' * border_width}{time_section}╗"
    if glitch_active:
        top = apply_glitch_to_string(top, glitch_intensity * 0.5)
    
    print(theme.BACKGROUND + " " * max(0, h_offset + wave_offset) + theme.BORDER_COLOR + top + theme.RESET)
    
    # Содержимое
    for i, line in enumerate(content[-(height - 2):]):
        line_offset = h_offset
        
        # Эффект сканирования
        if glitch_active and glitch_type == 'scan':
            scan_pos = int(time.time() * 20 % height)
            if i == scan_pos:
                line = apply_glitch_to_string(line, 0.8)
        
        # Волновой сдвиг для каждой строки
        if glitch_active and glitch_type == 'wave':
            line_offset += int(2 * abs(i - height/2) / height)
        
        if glitch_active and random.random() < glitch_intensity * 0.3:
            line_offset += random.randint(-1, 1)
        
        # Цвет линии с глитч-эффектом
        color = theme.TEXT_COLOR
        if glitch_active:
            if glitch_type == 'color_bleed':
                # Радужный эффект
                colors = [theme.RED, theme.YELLOW, theme.MAGENTA, theme.CYAN, theme.TEXT_COLOR]
                color = colors[i % len(colors)]
            elif random.random() < glitch_intensity * 0.4:
                color = random.choice([theme.RED, theme.YELLOW, theme.MAGENTA, theme.CYAN])
        
        formatted_line = f"{color}{line.ljust(width - 4)[:width - 4]}{theme.RESET}"
        if glitch_active:
            formatted_line = apply_glitch_to_string(formatted_line, glitch_intensity * 0.2)
        
        print(theme.BACKGROUND + " " * max(0, line_offset) + f"{theme.BORDER_COLOR}║{theme.RESET} {formatted_line} {theme.BORDER_COLOR}║{theme.RESET}")
    
    # Пустые строки с артефактами
    for j in range(height - 2 - len(content)):
        line_offset = h_offset
        if glitch_active and random.random() < glitch_intensity * 0.3:
            line_offset += random.randint(-1, 1)
        
        empty_space = ' ' * (width - 4)
        # Добавляем артефакты в пустые места
        if glitch_active:
            if glitch_type == 'static':
                # Статический шум
                for k in range(width - 4):
                    if random.random() < glitch_intensity * 0.3:
                        empty_space = empty_space[:k] + random.choice('·.,:;') + empty_space[k+1:]
            elif random.random() < glitch_intensity:
                artifact_count = random.randint(1, max(1, int(glitch_intensity * 10)))
                for _ in range(artifact_count):
                    pos = random.randint(0, width - 5)
                    empty_space = empty_space[:pos] + random.choice(ARTIFACT_CHARS) + empty_space[pos+1:]
        
        print(theme.BACKGROUND + " " * max(0, line_offset) + f"{theme.BORDER_COLOR}║{theme.RESET} {theme.DIM}{empty_space}{theme.RESET} {theme.BORDER_COLOR}║{theme.RESET}")
    
    # Нижняя граница
    bottom = f"╚{'═' * (width - 2)}╝"
    if glitch_active:
        bottom = apply_glitch_to_string(bottom, glitch_intensity * 0.5)
    print(theme.BACKGROUND + " " * max(0, h_offset) + theme.BORDER_COLOR + bottom + theme.RESET)

def draw_interface(input_preview=""):
    clear()
    
    # Мигание экрана (убрал sleep чтобы не зависать)
    if glitch_active and glitch_type == 'flicker' and random.random() < glitch_intensity * 0.2:
        print(theme.REVERSE + " " * WIDTH + theme.RESET)
        clear()
    
    draw_box("ONI", output_lines, HEIGHT, WIDTH)
    
    # Промпт с глитчами
    prompt_text = f"> {input_preview}"
    if glitch_active and random.random() < glitch_intensity * 0.3:
        prompt_text = apply_glitch_to_string(prompt_text, glitch_intensity * 0.4)
    
    prompt = f"\n{theme.DIM}{prompt_text}{theme.RESET}"
    print(prompt, end="", flush=True)

async def update_glitch_state():
    global glitch_active, glitch_intensity, glitch_type, last_glitch_time
    
    while True:
        current_time = time.time()
        
        # Случайная активация глитча (разные типы)
        if not glitch_active and random.random() < 0.008:  # 0.8% шанс (еще реже)
            glitch_active = True
            glitch_type = random.choice([
                'heavy', 'light', 'flicker', 'shift', 'corrupt', 
                'digital', 'wave', 'scan', 'static', 'color_bleed'
            ])
            
            if glitch_type == 'heavy':
                glitch_intensity = random.uniform(0.6, 0.9)
            elif glitch_type == 'light':
                glitch_intensity = random.uniform(0.1, 0.3)
            elif glitch_type == 'flicker':
                glitch_intensity = random.uniform(0.3, 0.5)
            elif glitch_type == 'shift':
                glitch_intensity = random.uniform(0.4, 0.7)
            elif glitch_type == 'corrupt':
                glitch_intensity = random.uniform(0.5, 0.8)
            elif glitch_type == 'digital':
                glitch_intensity = random.uniform(0.2, 0.4)
            elif glitch_type == 'wave':
                glitch_intensity = random.uniform(0.3, 0.6)
            elif glitch_type == 'scan':
                glitch_intensity = random.uniform(0.2, 0.5)
            elif glitch_type == 'static':
                glitch_intensity = random.uniform(0.4, 0.6)
            else:  # color_bleed
                glitch_intensity = random.uniform(0.3, 0.7)
                
            last_glitch_time = current_time
        
        # Обновление интенсивности глитча
        if glitch_active:
            time_since_start = current_time - last_glitch_time
            
            # Глитч длится 0.1-0.5 секунд
            if time_since_start > random.uniform(0.1, 0.5):
                glitch_active = False
                glitch_intensity = 0.0
            else:
                # Пульсация интенсивности
                if glitch_type in ['wave', 'scan']:
                    # Волновая пульсация
                    glitch_intensity = 0.5 + 0.4 * abs(time_since_start * 10 % 2 - 1)
                else:
                    glitch_intensity = min(1.0, glitch_intensity + random.uniform(-0.2, 0.3))
                    glitch_intensity = max(0.05, glitch_intensity)
        
        await asyncio.sleep(0.05)  # Обновление состояния 20 раз в секунду

async def render_loop():
    while True:
        async with input_lock:
            draw_interface(user_input)
        await asyncio.sleep(1/60)  # 60 FPS

async def read_input():
    global user_input
    
    while True:
        try:
            # Читаем ввод побайтово
            loop = asyncio.get_event_loop()
            key = await loop.run_in_executor(None, os.read, 0, 1)
            
            async with input_lock:
                if key == b'\n':  # Enter
                    if user_input.strip():
                        output_lines.append(f"Вы написали: {user_input}")
                        output_lines.append(f"Отправлено: {user_input}")
                    else:
                        output_lines.append(f"{theme.DIM}...пустой ввод...{theme.RESET}")
                    user_input = ""
                elif key == b'\x7f' or key == b'\x08':  # Backspace
                    user_input = user_input[:-1]
                elif key == b'\x03':  # Ctrl+C
                    raise KeyboardInterrupt
                elif key == b'\x1b':  # Escape sequences (ignore)
                    # Читаем остальную часть escape-последовательности
                    await loop.run_in_executor(None, os.read, 0, 10)
                elif ord(key) >= 32 and ord(key) < 127:  # Печатаемые символы
                    try:
                        user_input += key.decode('utf-8')
                    except:
                        pass
        except:
            await asyncio.sleep(0.01)

async def main():
    # Настройка терминала для неблокирующего ввода
    os.system("stty -echo -icanon")
    
    try:
        # Запускаем все задачи параллельно
        await asyncio.gather(
            render_loop(),
            read_input(),
            update_glitch_state()
        )
    finally:
        # Восстанавливаем настройки терминала
        os.system("stty echo icanon")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        os.system("stty echo icanon")  # Восстанавливаем терминал
        print("\n" + theme.BORDER_COLOR + "[Отключено от сети]" + theme.RESET)