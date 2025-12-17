#include "config.h"
#include "uart.h"
#include "display.h" // Needs to call Display functions
#include <string.h>
#include <stdlib.h>

volatile char rx_str[10];
volatile int rx_idx = 0;

void UART_Init(void) {
    TRISCbits.TRISC6 = 1; TRISCbits.TRISC7 = 1;
    TXSTAbits.SYNC = 0; BAUDCONbits.BRG16 = 0; TXSTAbits.BRGH = 1; SPBRG = 25;      
    RCSTAbits.SPEN = 1; TXSTAbits.TXEN = 1; RCSTAbits.CREN = 1;
    PIE1bits.RCIE = 1; 
}

void UART_Write_Text(char *text) {
    for(int i=0; text[i]!='\0'; i++) {
        while(!TRMT);
        TXREG = text[i];
    }
}

void UART_ISR_Handler(void) {
    if (PIR1bits.RCIF) {
        char rx = RCREG;
        
        // Single Char Commands (LEDs)
        if (rx == 'G' || rx == 'P' || rx == 'E' || rx == 'X') {
            if(rx=='X'){Display_Update_Score(0);}
            Display_Set_LED(rx);
            rx_idx = 0; // RESET index so this char doesn't corrupt the next string
            return;     // Stop processing this character
        }
        
        // String Parsing (Score)
        if (rx == '\n' || rx == '\r') {
            rx_str[rx_idx] = '\0'; 
            rx_idx = 0;
            // Check matches "SCR:"
            if (strncmp((char*)rx_str, "SCR:", 4) == 0) {
                int new_score = atoi((char*)&rx_str[4]);
                Display_Update_Score(new_score);
            }
        } else if (rx_idx < 9) {
            rx_str[rx_idx++] = rx;
        }
    }
}