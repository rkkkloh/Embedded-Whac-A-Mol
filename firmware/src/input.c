/**
 * @file input.c
 * @brief Implementation of Input handling functions.
 */

#include "config.h"
#include "inputs.h"
#include "uart.h"
#include <stdio.h>

// Global flag set by ISR when Confirm Button is pressed
volatile int btn_confirm_flag = 0;

// State tracker for game buttons to prevent repeated triggering
int btn_states[9] = {0}; 

// Buffer for UART formatting
char buf[20];

void Inputs_Init(void) {
    // --- GPIO Configuration ---
    TRISD = 0xFF;         // PORTD (Buttons 0-7) as Inputs
    TRISEbits.TRISE0 = 1; // RE0 (Button 8) as Input
    TRISBbits.TRISB0 = 1; // RB0 (Confirm Button) as Input
    
    // --- ADC Configuration ---
    TRISAbits.TRISA0 = 1; // Set RA0 as Input for Potentiometer
    ADCON1 = 0x0E;        // Configure AN0 as Analog, others Digital
    ADCON0 = 0x01;        // Enable ADC module, Channel 0
    ADCON2 = 0x92;        // Right justify, 4 TAD, Fosc/32
    
    // --- Interrupt Configuration ---
    // Setup INT0 (RB0) for Confirm Button
    INTCON2bits.INTEDG0 = 0; // Trigger on Falling Edge
    INTCONbits.INT0IF = 0;   // Clear Flag
    INTCONbits.INT0IE = 1;   // Enable INT0 Interrupt
}

int ADC_Read(void) {
    // Start Conversion
    ADCON0bits.GO = 1; 
    // Wait for conversion to complete
    while(ADCON0bits.GO);
    // Return 10-bit result
    return ((ADRESH << 8) + ADRESL);
}

void Inputs_ISR_Handler(void) {
    // Check INT0 (Confirm Button) Flag
    if (INTCONbits.INT0IF) {
        btn_confirm_flag = 1; // Set flag for Main Loop
        INTCONbits.INT0IF = 0; // Clear Flag
    }
}

void Check_Matrix_Buttons(void) {
    // --- Scan PORTD (Buttons 0-7) ---
    for(int i=0; i<8; i++) {
        // Active Low: Check if bit is 0
        if ( (PORTD >> i) & 1 ) {
            btn_states[i] = 0; // Button Released
        }
        else {
            // Button Pressed
            if (btn_states[i] == 0) {
                // Send event only on initial press (Rising Edge logic)
                sprintf(buf, "BTN:%d\r\n", i);
                UART_Write_Text(buf);
                btn_states[i] = 1; // Mark as pressed
                __delay_ms(50);    // Simple Debounce
            }
        }
    }
    
    // --- Scan PORTE (Button 8) ---
    if (PORTEbits.RE0 == 1) {
        btn_states[8] = 0; // Released
    }
    else if (btn_states[8] == 0) {
        // Pressed
        UART_Write_Text("BTN:8\r\n");
        btn_states[8] = 1;
        __delay_ms(50); // Debounce
    }
}