# 🎮 Cyber-Physical Whac-A-Mole (Embedded System Project)

![Language](https://img.shields.io/badge/language-C%20%7C%20Python-blue)
![Platform](https://img.shields.io/badge/platform-PIC18F4520%20%7C%20Windows-green)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

> **Course:** Embedded Operating Systems / Microcontroller System Design
> **Institution:** National Cheng Kung University (NCKU)
> **Department:** Computer Science and Information Engineering (CSIE)

## 📖 Abstract
This project implements a **Cyber-Physical System (CPS)** game: "Whac-A-Mole". It integrates a **PIC18F4520 microcontroller** for hardware control (buttons, LEDs) and a **Python-based GUI** for game logic, rendering, and audio processing. The system demonstrates bidirectional communication via **UART/Bluetooth (HC-05)**, ensuring low-latency synchronization between the physical controller and the digital game world.

---

## 🌟 Key Features
* **Bidirectional Communication:** Real-time synchronization between PC and MCU via UART (9600 baud).
* **Hardware Interrupt Handling:** Efficient utilization of High-Priority Interrupts for UART reception and Timer0 (7-Seg scanning).
* **Dynamic Difficulty:** Game speed adjusts automatically based on the player's score and selected difficulty level.
* **Visual Feedback:**
    * **7-Segment Display:** Shows current score on the hardware controller.
    * **RGB LEDs:** Indicates system state (Green=Play, Yellow=Pause, Red=Menu).
* **Robust GUI:** Built with `pygame`, featuring clean UI, animations, and background threading for connection stability.

---

## 🛠️ System Architecture

### 1. Hardware Pin Map (PIC18F4520)

| Component | Pin Name | Pin Number | Function |
| :--- | :--- | :--- | :--- |
| **UART (Bluetooth)** | RC6 (TX) / RC7 (RX) | Pin 25 / 26 | Data transmission with PC |
| **Game Buttons (0-7)** | PORTD (RD0-RD7) | Pin 19-22, 27-30 | Mole inputs (Active Low) |
| **Game Button 8** | RE0 | Pin 8 | Mole input (Active Low) |
| **Confirm Button** | RB0 (INT0) | Pin 33 | Menu confirmation / Pause |
| **Status LEDs** | RB3 / RB4 / RB5 | Pin 36-38 | Green / Yellow / Red indicators |
| **7-Segment (Segs)** | PORTC (RC0-RC5) | Pin 15-18, 23-24 | Segments A-F |
| **7-Segment (Seg G)**| RB2 | Pin 35 | Segment G (Moved to avoid UART conflict) |
| **7-Segment (Common)**| RA1-RA4 | Pin 3-6 | Digit selection (Multiplexing) |
| **Potentiometer** | RA0 (AN0) | Pin 2 | Menu navigation / Difficulty select |

### 2. Software Stack
* **Firmware:** C (MPLAB X IDE, XC8 Compiler)
    * Utilizes `ISR` for non-blocking operations.
    * Handles 7-segment multiplexing via `Timer0`.
* **Software:** Python 3.11
    * `pygame`: Rendering engine and input handling.
    * `pyserial`: Serial communication interface.
    * `threading`: Handles connection logic without freezing the UI.

---

## 🚀 Installation & Usage

### Prerequisites
* Python 3.8+
* MPLAB X IDE (to compile and flash firmware)
* PICkit 3/4 Programmer (or compatible debugger)

### Step 1: Hardware Setup
1.  Connect the **HC-05 Bluetooth module** to the PIC18F4520 (VCC=5V, GND=GND, TX->RC7, RX->RC6).
2.  Connect Buttons, LEDs, and 7-Segment Display according to the Pin Map above.
3.  Ensure the circuit is powered (5V).

### Step 2: Firmware Setup
1.  Open the `firmware/` project in **MPLAB X IDE**.
2.  Build the project using the **XC8 Compiler**.
3.  Connect your **PICkit** to the microcontroller.
4.  Click **Make and Program Device** to flash the code onto the PIC18F4520.

### Step 3: Software Setup
```bash
# Clone the repository
git clone https://github.com/rkkkloh/Embedded-Whac-A-Mol.git

# Navigate to the directory
cd Embedded-Whac-A-Mol

# Install dependencies
pip install pygame pyserial