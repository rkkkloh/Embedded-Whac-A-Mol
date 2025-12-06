# 🎮 虛實整合打地鼠 (Cyber-Physical Whac-A-Mole)

> NCKU CSIE Embedded System Project - Group 3

本專案結合 **PIC18F4520** 嵌入式系統與 **Python 音樂節奏演算法**，打造具備聲光效果的互動打地鼠遊戲。

## 👥 團隊成員
* **後端演算法**: 羅睿康 (Algorithm & Logic)
* **前端介面**: 陳冠謙 (GUI Design)
* **韌體開發**: 鄭永順 (Firmware & I/O)
* **硬體建置**: 彭志光 (Circuit & Testing)

## 🛠️ 系統架構
* **Hardware**: PIC18F4520, LEDs, Buttons, HC-05 Bluetooth
* **Software**: Python (Librosa, PySerial, Tkinter/PyQt)
* **Communication**: UART (9600 baud rate)

## 🚀 如何執行
1. 安裝 Python 套件: `pip install -r Software/requirements.txt`
2. 連接硬體藍牙
3. 執行遊戲: `python Software/main.py`# Whac-A-Mole Project
