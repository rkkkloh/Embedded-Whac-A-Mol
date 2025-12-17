/**
 * @file uart.c
 * @brief Implementation of UART communication.
 */

#include "config.h"
#include "uart.h"
#include "display.h" // Needed to update Display based on RX
#include <string.h>
#include <stdlib.h>

// Receive buffer for parsing commands (e.g., "SCR:100")
volatile char rx_str[10];
volatile int rx_idx = 0;

void UART_Init(void) {
    // Configure IO pins
    TRISCbits.TRISC6 = 1; // TX usually driven by module, but set as input/output depending on datasheet recommendations
    TRISCbits.TRISC7 = 1; // RX Must be Input
    
    // --- Baud Rate Generation ---
    // Formula: Baud = Fosc / (16 * (SPBRG + 1))
    // Target: 9600, Fosc: 4MHz
    TXSTAbits.SYNC = 0;      // Asynchronous mode
    BAUDCONbits.BRG16 = 0;   // 8-bit BRG
    TXSTAbits.BRGH = 1;      // High Speed
    SPBRG = 25;              // Calculated value for 9600
    
    // --- Enable Module ---
    RCSTAbits.SPEN = 1;      // Serial Port Enable
    TXSTAbits.TXEN = 1;      // Transmit Enable
    RCSTAbits.CREN = 1;      // Continuous Receive Enable
    
    // --- Interrupts ---
    PIE1bits.RCIE = 1;       // Enable Receive Interrupt
}

void UART_Write_Text(char *text) {
    // Loop through string until null terminator
    for(int i=0; text[i]!='\0'; i++) {
        while(!TXSTAbits.TRMT); // Wait until Transmit Shift Register is empty
        TXREG = text[i];        // Load data to transmit
    }
}

void UART_ISR_Handler(void) {
    // Check Receive Interrupt Flag
    if (PIR1bits.RCIF) {
        char rx = RCREG; // Read data (clears flag)
        
        // --- Single Character Commands ---
        // Control LEDs based on Game State
        if (rx == 'G' || rx == 'P' || rx == 'E' || rx == 'X') {
            if(rx == 'X'){ 
                Display_Update_Score(0); // Clear score on exit
            }
            Display_Set_LED(rx);
            rx_idx = 0; // Reset buffer
        }
        
        // --- String Parsing for Score ---
        // Expecting format: "SCR:xxxx\n"
        else if (rx == '\n' || rx == '\r') {
            rx_str[rx_idx] = '\0'; // Null-terminate
            rx_idx = 0;
            
            // Check prefix
            if (strncmp((char*)rx_str, "SCR:", 4) == 0) {
                int new_score = atoi((char*)&rx_str[4]);
                Display_Update_Score(new_score);
            }
        } 
        else if (rx_idx < 9) {
            // Store char in buffer
            rx_str[rx_idx++] = rx;
        }
    }
}