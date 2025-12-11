#include <xc.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#pragma config OSC = INTIO67, WDT = OFF, PBADEN = OFF, LVP = OFF, MCLRE = OFF
#define _XTAL_FREQ 4000000 
#define POT_THRESHOLD 15 

// --- 7-SEGMENT PATTERNS (Common Anode) ---
// 0 = ON, 1 = OFF
// Original (Cathode): 0x3F (0011 1111) -> 0
// New (Anode): ~0x3F (1100 0000) -> 0
const unsigned char SEG_MAP[10] = {
    0xC0, // 0
    0xF9, // 1
    0xA4, // 2
    0xB0, // 3
    0x99, // 4
    0x92, // 5
    0x82, // 6
    0xF8, // 7
    0x80, // 8
    0x90  // 9
};

volatile int btn_confirm_flag = 0;
volatile char display_buffer[4] = {0, 0, 0, 0}; 
volatile int digit_scan_index = 0; 

// UART Buffer
volatile char rx_str[10];
volatile int rx_idx = 0;

void Update_Display_Buffer(int number) {
    if (number > 9999) number = 9999;
    display_buffer[0] = (number / 1000) % 10;
    display_buffer[1] = (number / 100) % 10;
    display_buffer[2] = (number / 10) % 10;
    display_buffer[3] = number % 10;
}

void UART_Init() {
    TRISCbits.TRISC6 = 0; TRISCbits.TRISC7 = 1;
    TXSTAbits.SYNC = 0; BAUDCONbits.BRG16 = 0; TXSTAbits.BRGH = 0; SPBRG = 51;      
    RCSTAbits.SPEN = 1; TXSTAbits.TXEN = 1; RCSTAbits.CREN = 1;
    PIE1bits.RCIE = 1; 
}

void UART_Write_Text(char *text) {
    for(int i=0; text[i]!='\0'; i++) {
        while(!TRMT);
        TXREG = text[i];
    }
}

void ADC_Init() {
    TRISAbits.TRISA0 = 1; ADCON1 = 0x0E; ADCON0 = 0x01; ADCON2 = 0x92;
}

int ADC_Read() {
    ADCON0bits.GO = 1; while(ADCON0bits.GO);
    return ((ADRESH << 8) + ADRESL);
}

void INT0_Init() {
    TRISBbits.TRISB0 = 1; INTCON2bits.INTEDG0 = 0; 
    INTCONbits.INT0IF = 0; INTCONbits.INT0IE = 1; 
}

void TMR0_Init() {
    T0CONbits.T08BIT = 0; T0CONbits.T0CS = 0; T0CONbits.PSA = 0;    
    T0CONbits.T0PS = 0b010; // 1:8 Prescaler
    TMR0H = 0xFC; TMR0L = 0x17; // 5ms interrupt
    INTCONbits.TMR0IE = 1; T0CONbits.TMR0ON = 1;
}

void __interrupt() ISR(void) {
    
    // 1. UART RX
    if (PIR1bits.RCIF) {
        char rx = RCREG;
        if (rx == 'G') { LATBbits.LATB3=1; LATBbits.LATB4=0; LATBbits.LATB5=0; }
        else if (rx == 'P') { LATBbits.LATB3=0; LATBbits.LATB4=1; LATBbits.LATB5=0; }
        else if (rx == 'E') { LATBbits.LATB3=0; LATBbits.LATB4=0; LATBbits.LATB5=1; }
        else if (rx == 'X') { LATBbits.LATB3=0; LATBbits.LATB4=0; LATBbits.LATB5=0; }
        
        if (rx == '\n' || rx == '\r') {
            rx_str[rx_idx] = '\0'; 
            rx_idx = 0;
            if (strncmp(rx_str, "SCR:", 4) == 0) {
                int new_score = atoi(&rx_str[4]);
                Update_Display_Buffer(new_score);
            }
        } else if (rx_idx < 9) {
            rx_str[rx_idx++] = rx;
        }
    }

    // 2. BUTTON INTERRUPT
    if (INTCONbits.INT0IF) {
        btn_confirm_flag = 1;
        INTCONbits.INT0IF = 0;
    }

    // 3. TIMER0 INTERRUPT (DISPLAY REFRESH)
    if (INTCONbits.TMR0IF) {
        TMR0H = 0xFC; TMR0L = 0x17;
        
        // A. Turn OFF all Digits first (Ghosting prevention)
        // Common Anode: OFF = LOW (0)
        LATA &= 0xE1; // Clear RA1, RA2, RA3, RA4 (Keep RA0 safe)
        
        // B. Set Segments (Common Anode: 0 = ON)
        int num = display_buffer[digit_scan_index];
        unsigned char pattern = SEG_MAP[num];
        
        // Update RC0-RC5 (Segments A-F)
        // We mask out bits 0-5 of PORTC and replace them
        LATC = (LATC & 0xC0) | (pattern & 0x3F); 
        
        // Update RB2 (Segment G is bit 6 of pattern)
        LATBbits.LATB2 = (pattern >> 6) & 0x01;
        
        // C. Turn ON current Digit (Common Anode: ON = HIGH)
        switch(digit_scan_index) {
            case 0: LATAbits.LATA1 = 1; break; // Digit 1
            case 1: LATAbits.LATA2 = 1; break; // Digit 2
            case 2: LATAbits.LATA3 = 1; break; // Digit 3
            case 3: LATAbits.LATA4 = 1; break; // Digit 4
        }
        
        digit_scan_index++;
        if (digit_scan_index > 3) digit_scan_index = 0;
        
        INTCONbits.TMR0IF = 0;
    }
}

void main(void) {
    OSCCONbits.IRCF = 0b110; 

    // Pin Directions
    TRISD = 0xFF;         // Game Buttons 0-7 (Input)
    TRISEbits.TRISE0 = 1; // Game Button 8 (Input)
    TRISBbits.TRISB0 = 1; // Confirm Button (Input)
    
    // LED Outputs
    TRISBbits.TRISB3 = 0; TRISBbits.TRISB4 = 0; TRISBbits.TRISB5 = 0;
    
    // 7-Segment Outputs
    TRISCbits.TRISC0 = 0; TRISCbits.TRISC1 = 0; TRISCbits.TRISC2 = 0;
    TRISCbits.TRISC3 = 0; TRISCbits.TRISC4 = 0; TRISCbits.TRISC5 = 0;
    TRISBbits.TRISB2 = 0; 
    
    // Digit Select Outputs (RA1-RA4)
    TRISAbits.TRISA1 = 0; TRISAbits.TRISA2 = 0;
    TRISAbits.TRISA3 = 0; TRISAbits.TRISA4 = 0;
    
    // Initial State
    LATBbits.LATB5 = 1; // Red LED
    LATA &= 0xE1;       // Digits Off
    Update_Display_Buffer(0000);

    UART_Init();
    ADC_Init();
    INT0_Init(); 
    TMR0_Init();
    
    INTCONbits.PEIE = 1; INTCONbits.GIE = 1;
    
    char buffer[30];
    int pot_val = 0;
    int last_pot_val = -100; 
    int btn_states[9] = {0}; 

    UART_Write_Text("System Ready.\r\n");

    while(1) {
        // Potentiometer
        pot_val = ADC_Read();
        if (abs(pot_val - last_pot_val) > POT_THRESHOLD) {
            sprintf(buffer, "POT:%d\r\n", pot_val);
            UART_Write_Text(buffer);
            last_pot_val = pot_val; 
        }

        // Confirm Button
        if (btn_confirm_flag) {
            UART_Write_Text("BTN:CONFIRM\r\n");
            __delay_ms(300);
            btn_confirm_flag = 0;
        }

        // Game Buttons
        for(int i=0; i<8; i++) {
            if ( (PORTD >> i) & 1 ) btn_states[i] = 0; 
            else {
                if (btn_states[i] == 0) {
                    sprintf(buffer, "BTN:%d\r\n", i);
                    UART_Write_Text(buffer);
                    btn_states[i] = 1;
                    __delay_ms(50); 
                }
            }
        }
        
        if (PORTEbits.RE0 == 1) btn_states[8] = 0;
        else if (btn_states[8] == 0) {
            UART_Write_Text("BTN:8\r\n");
            btn_states[8] = 1;
            __delay_ms(50);
        }

        __delay_ms(50); 
    }
}