#include "config.h"
#include "display.h"

// --- 7-SEGMENT MAP (Common Anode: 0=ON) ---
const unsigned char SEG_MAP[10] = {
    0xC0, 0xF9, 0xA4, 0xB0, 0x99, 
    0x92, 0x82, 0xF8, 0x80, 0x90
};

volatile char display_buffer[4] = {0}; 
volatile int digit_scan_index = 0; 

void Display_Init(void) {
    RCONbits.IPEN = 1;
    // Port Directions (Outputs)
    TRISC &= 0xC0; // RC0-RC5 Output (Segments)
    TRISBbits.TRISB2 = 0; // Segment G Output
    TRISBbits.TRISB3 = 0; TRISBbits.TRISB4 = 0; TRISBbits.TRISB5 = 0; // LEDs
    
    // Digit Selects
    TRISAbits.TRISA1 = 0; TRISAbits.TRISA2 = 0;
    TRISAbits.TRISA3 = 0; TRISAbits.TRISA4 = 0;
    LATB &= 0b11000111;
    // Initial State
    // LED_RED = 1; 
    LATA &= 0xE1; // Digits Off
    Display_Update_Score(0);

    T0CONbits.T08BIT = 0; T0CONbits.T0CS = 0; T0CONbits.PSA = 0;    
    T0CONbits.T0PS = 0b000; 
    TMR0H = 0xFC; TMR0L = 0x18; 
    INTCONbits.TMR0IE = 1; T0CONbits.TMR0ON = 1;
    INTCON2bits.TMR0IP = 1;
}

void Display_Update_Score(int number) {
    if (number > 9999) number = 9999;
    display_buffer[0] = (number / 1000) % 10;
    display_buffer[1] = (number / 100) % 10;
    display_buffer[2] = (number / 10) % 10;
    display_buffer[3] = number % 10;
}

void Display_Set_LED(char color) {
    LED_GREEN = 0; LED_YELLOW = 0; LED_RED = 0;
    if (color == 'G') LED_GREEN = 1;
    else if (color == 'P') LED_YELLOW = 1;
    else if (color == 'E') LED_RED = 1;
}

void Display_ISR_Handler(void) {
    if (INTCONbits.TMR0IF) {
        TMR0H = 0xFC; TMR0L = 0x18;
        
        // A. Turn OFF all Digits (Common Anode: High=OFF)
        LATA &= 0xE1; // 11100001 
        
        // B. Set Segments (Common Anode: Low=ON)
        int num = display_buffer[digit_scan_index];
        unsigned char pattern = SEG_MAP[num];
        
        LATC = (LATC & 0xC0) | (pattern & 0x3F); 
        SEG_G = (pattern >> 6) & 0x01;
        
        // C. Turn ON current Digit (Common Anode: High=ON)
        switch(digit_scan_index) {
            case 0: DIGIT_1 = 1; break;
            case 1: DIGIT_2 = 1; break;
            case 2: DIGIT_3 = 1; break;
            case 3: DIGIT_4 = 1; break;
        }
        
        digit_scan_index++;
        if (digit_scan_index > 3) digit_scan_index = 0;
        
        INTCONbits.TMR0IF = 0;
    }
}