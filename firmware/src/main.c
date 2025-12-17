#include "config.h"
#include "display.h"
#include "uart.h"
#include "inputs.h"
#include <stdio.h>
#include <stdlib.h>

// Config Bits
#pragma config OSC = INTIO67, WDT = OFF, PBADEN = OFF, LVP = OFF, MCLRE = OFF

// Central Interrupt Manager
void __interrupt(high_priority) Hi_ISR(void) {
    UART_ISR_Handler();
    Inputs_ISR_Handler();
    Display_ISR_Handler();
}

void main(void) {
    OSCCONbits.IRCF = 0b110; // 4 MHz

    // Initialize Modules
    Display_Init();
    UART_Init();
    Inputs_Init();
    
    // Enable Global Interrupts
    INTCONbits.PEIE = 1; 
    INTCONbits.GIE = 1;
    
    char buffer[30];
    int pot_val = 0;
    int last_pot_val = -100; 

    UART_Write_Text("System Ready.\r\n");

    while(1) {
        // 1. Check Potentiometer
        pot_val = ADC_Read();
        if (abs(pot_val - last_pot_val) > POT_THRESHOLD) {
            sprintf(buffer, "POT:%d\r\n", pot_val);
            UART_Write_Text(buffer);
            last_pot_val = pot_val; 
        }

        // 2. Check Confirm Button Flag
        if (btn_confirm_flag) {
            UART_Write_Text("BTN:CONFIRM\r\n");
            __delay_ms(300);
            btn_confirm_flag = 0;
        }

        // 3. Check Game Buttons
        Check_Matrix_Buttons();

        __delay_ms(20); 
    }
}