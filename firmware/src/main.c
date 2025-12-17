/**
 * @file main.c
 * @brief Main Entry point for the PIC18F4520 Firmware.
 * @details Coordinates ADC reading, Button scanning, and calling initialization routines.
 * @author Group 8
 */

#include "config.h"
#include "display.h"
#include "uart.h"
#include "inputs.h"
#include <stdio.h>
#include <stdlib.h>

// --- Configuration Bits ---
// INTIO67: Internal Oscillator
// WDT=OFF: Watchdog Timer Disabled
// LVP=OFF: Low Voltage Programming Disabled
#pragma config OSC = INTIO67, WDT = OFF, PBADEN = OFF, LVP = OFF, MCLRE = OFF

/**
 * @brief High Priority Interrupt Service Routine.
 * Delegates tasks to specific module handlers.
 */
void __interrupt(high_priority) Hi_ISR(void) {
    UART_ISR_Handler();     // Handle Bluetooth RX
    Inputs_ISR_Handler();   // Handle Confirm Button
    Display_ISR_Handler();  // Handle 7-Seg Refresh
}

void main(void) {
    // 1. Oscillator Setup
    OSCCONbits.IRCF = 0b110; // Set Internal Oscillator to 4 MHz

    // 2. Initialize Modules
    Display_Init(); // Setup LEDs and 7-Segment
    UART_Init();    // Setup Bluetooth
    Inputs_Init();  // Setup Buttons and ADC
    
    // 3. Enable Global Interrupts
    INTCONbits.PEIE = 1; // Peripheral Interrupts
    INTCONbits.GIE = 1;  // Global Interrupts
    
    char buffer[30];
    int pot_val = 0;
    int last_pot_val = -100; 

    // Notify PC that system is online
    UART_Write_Text("System Ready.\r\n");

    // --- Main Loop ---
    while(1) {
        // Task 1: Check Potentiometer
        pot_val = ADC_Read();
        // Send updates only if value changes significantly (Threshold)
        if (abs(pot_val - last_pot_val) > POT_THRESHOLD) {
            sprintf(buffer, "POT:%d\r\n", pot_val);
            UART_Write_Text(buffer);
            last_pot_val = pot_val; 
        }

        // Task 2: Check Confirm Button (Flag from ISR)
        if (btn_confirm_flag) {
            UART_Write_Text("BTN:CONFIRM\r\n");
            __delay_ms(300); // Main loop debounce
            btn_confirm_flag = 0;
        }

        // Task 3: Check Game Buttons (Matrix Scan)
        Check_Matrix_Buttons();

        // Small delay to stabilize main loop
        __delay_ms(10); 
    }
}