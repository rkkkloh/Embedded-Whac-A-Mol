#include "config.h"
#include "inputs.h"
#include "uart.h"
#include <stdio.h>

volatile int btn_confirm_flag = 0;
int btn_states[9] = {0}; 
char buf[20];

void Inputs_Init(void) {
    // Directions
    TRISD = 0xFF;         // Game Buttons 0-7
    TRISEbits.TRISE0 = 1; // Game Button 8
    TRISBbits.TRISB0 = 1; // Confirm Button
    
    // ADC
    TRISAbits.TRISA0 = 1; ADCON1 = 0x0E; ADCON0 = 0x01; ADCON2 = 0x92;
    
    // Interrupt RB0
    INTCON2bits.INTEDG0 = 0; INTCONbits.INT0IF = 0; INTCONbits.INT0IE = 1; 
}

int ADC_Read(void) {
    ADCON0bits.GO = 1; while(ADCON0bits.GO);
    return ((ADRESH << 8) + ADRESL);
}

void Inputs_ISR_Handler(void) {
    if (INTCONbits.INT0IF) {
        btn_confirm_flag = 1;
        INTCONbits.INT0IF = 0;
    }
}

void Check_Matrix_Buttons(void) {
    // 0-7 on PORTD
    for(int i=0; i<8; i++) {
        if ( (PORTD >> i) & 1 ) btn_states[i] = 0; 
        else {
            if (btn_states[i] == 0) {
                sprintf(buf, "BTN:%d\r\n", i);
                UART_Write_Text(buf);
                btn_states[i] = 1;
                __delay_ms(50); 
            }
        }
    }
    // 8 on RE0
    if (PORTEbits.RE0 == 1) btn_states[8] = 0;
    else if (btn_states[8] == 0) {
        UART_Write_Text("BTN:8\r\n");
        btn_states[8] = 1;
        __delay_ms(50);
    }
}