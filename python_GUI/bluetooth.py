import pygame
import serial
import random
import sys
import os
import threading
from flask import Flask, request
import logging

# ==========================================
# 1. 網路與通訊設定
# ==========================================
# [Bluetooth] Mac 路徑 (若不接 PIC 也可以跑，會自動進模擬模式)
SERIAL_PORT = '/dev/tty.HC-06-DevB'  
BAUD_RATE = 9600

# [Wi-Fi Server] 設定
app = Flask(__name__)
# 關閉 Flask 的啟動訊息，避免洗版終端機
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# ==========================================
# 2. 全域變數 (用於執行緒間溝通)
# ==========================================
# 這裡存放從 Wi-Fi 收到的指令，主遊戲迴圈會來讀取
wifi_command_queue = []

# ==========================================
# 3. Flask Web Server (手機對接窗口)
# ==========================================
@app.route('/action', methods=['GET'])
def handle_action():
    """
    手機端呼叫範例: 
    http://<電腦IP>:5000/action?type=hit&val=0 (打第0洞)
    http://<電腦IP>:5000/action?type=mode&val=hard (換模式)
    http://<電腦IP>:5000/action?type=btn&val=confirm (確認/開始)
    """
    cmd_type = request.args.get('type')
    val = request.args.get('val')
    
    # 將指令放入佇列，讓 Pygame 主迴圈去處理
    if cmd_type and val:
        wifi_command_queue.append((cmd_type, val))
        return "OK", 200
    return "Error", 400

def run_flask():
    # host='0.0.0.0' 代表允許區域網路內的所有裝置連線
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

# ==========================================
# 4. 遊戲核心 (Pygame)
# ==========================================
# ... (這裡保留原本的顏色、參數設定，為了節省篇幅省略部分常數定義) ...
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
COLOR_BG = (30, 30, 30)
COLOR_MOLE = (255, 100, 100)
COLOR_HOLE = (80, 80, 80)
# ...

class GameState:
    def __init__(self):
        self.state = 0 # MENU
        self.score = 0
        self.lives = 3
        self.difficulty = 0
        self.current_mole_index = -1
        # ... 其他初始化變數同前一版 ...

    # ... (保留原本的 spawn_mole, handle_hit 等邏輯) ...

    def process_external_input(self, cmd_type, val):
        """ 統一處理來自 Bluetooth 或 Wi-Fi 的指令 """
        print(f"Command: {cmd_type} -> {val}")
        
        # 處理打擊指令
        if cmd_type == 'hit':
            try:
                idx = int(val)
                # 只有在遊戲進行中才算分
                if self.state == 1: # PLAYING
                    self.handle_hit(idx)
            except: pass

        # 處理按鈕/確認指令
        elif cmd_type == 'btn' and val == 'confirm':
            if self.state == 0: # MENU
                self.state = 1 # PLAYING
                self.score = 0
                self.lives = 3
                self.spawn_mole()
            elif self.state == 2: # GAMEOVER
                self.state = 0 # Back to MENU

        # 處理模式切換 (手機專用)
        elif cmd_type == 'mode':
            if val == 'easy': self.difficulty = 0
            elif val == 'medium': self.difficulty = 1
            elif val == 'hard': self.difficulty = 2

# ==========================================
# 5. 主程式啟動
# ==========================================
if __name__ == '__main__':
    # A. 啟動 Wi-Fi Server 執行緒
    t = threading.Thread(target=run_flask)
    t.daemon = True # 設定為守護執行緒，主程式關閉時它也會自動關閉
    t.start()

    print("=== Wi-Fi Server Started on Port 5000 ===")
    print("Please connect mobile to the same Wi-Fi and send requests.")

    # B. 初始化 Pygame & Serial
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    game = GameState()

    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.05)
    except:
        ser = None

    running = True
    while running:
        # 1. 處理 Wi-Fi 佇列指令
        while wifi_command_queue:
            cmd_type, val = wifi_command_queue.pop(0)
            game.process_external_input(cmd_type, val)

        # 2. 處理 Bluetooth Serial 指令
        if ser and ser.in_waiting:
            try:
                line = ser.readline().decode().strip()
                if line.startswith("BTN:"):
                    # 轉換格式給統一接口
                    idx = line.split(":")[1]
                    if idx == 'CONFIRM':
                        game.process_external_input('btn', 'confirm')
                    else:
                        game.process_external_input('hit', idx)
            except: pass

        # 3. 處理 Pygame 事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # 鍵盤測試用
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1: game.process_external_input('hit', '0')

        # 4. 更新畫面
        # ... (同前一版 update & draw) ...
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()