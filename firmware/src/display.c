/**
 * @file display.c
 * @brief Implementation of Display functions.
 * Handles 7-Segment Multiplexing via Timer0 Interrupt.
 */

#include "config.h"
#include "display.h"

// --- 7-SEGMENT PATTERN MAP (Common Anode) ---
// Index 0-9 corresponds to numbers 0-9.
// 0=Segment ON, 1=Segment OFF (for Common Anode direct drive logic typically)
const unsigned char SEG_MAP[10] = {
    0xC0, 0xF9, 0xA4, 0xB0, 0x99, 
    0x92, 0x82, 0xF8, 0x80, 0x90
};

// Buffer to hold digits [Thousands, Hundreds, Tens, Ones]
volatile char display_buffer[4] = {0, 0, 0, 0}; 
// Current digit being refreshed (0-3)
volatile int digit_scan_index = 0; 

void Display_Init(void) {
    // Enable Interrupt Priority logic
    RCONbits.IPEN = 1;

    // --- IO Configuration ---
    // Configure RC0-RC5 as Outputs (Segments A-F)
    TRISC &= 0xC0; 
    
    // Configure RB2 as Output (Segment G)
    TRISBbits.TRISB2 = 0; 
    
    // Configure LED pins as Outputs
    TRISBbits.TRISB3 = 0; 
    TRISBbits.TRISB4 = 0; 
    TRISBbits.TRISB5 = 0; 
    
    // Configure Digit Select pins (RA1-RA4) as Outputs
    TRISAbits.TRISA1 = 0; TRISAbits.TRISA2 = 0;
    TRISAbits.TRISA3 = 0; TRISAbits.TRISA4 = 0;

    // Turn off Digits initially
    LATA &= 0xE1; 
    
    // --- Timer0 Initialization for Multiplexing ---
    // Setup Timer0: 8-bit mode, Internal Clock, 1:2 Prescaler
    T0CONbits.T08BIT = 1;   // 8-bit timer
    T0CONbits.T0CS = 0;     // Internal instruction cycle clock
    T0CONbits.PSA = 0;      // Prescaler assigned
    T0CONbits.T0PS = 0b000; // 1:2 Prescaler (approx 5ms interval)
    
    // Load initial value
    TMR0H = 0xFC; 
    TMR0L = 0x18; 
    
    // Enable Timer0 Interrupts
    INTCONbits.TMR0IE = 1; 
    INTCON2bits.TMR0IP = 1; // High Priority
    T0CONbits.TMR0ON = 1;   // Start Timer
}

void Display_Update_Score(int number) {
    // Clamp score to 9999
    if (number > 9999) number = 9999;
    
    // Split number into digits
    display_buffer[0] = (number / 1000) % 10;
    display_buffer[1] = (number / 100) % 10;
    display_buffer[2] = (number / 10) % 10;
    display_buffer[3] = number % 10;
}

void Display_Set_LED(char color) {
    // Reset all LEDs
    LED_GREEN = 0; LED_YELLOW = 0; LED_RED = 0;
    
    // Set LED based on command char
    if (color == 'G') LED_GREEN = 1;
    else if (color == 'P') LED_YELLOW = 1;
    else if (color == 'E') LED_RED = 1;
}

void Display_ISR_Handler(void) {
    // Check Timer0 Overflow Flag
    if (INTCONbits.TMR0IF) {
        // Reset Timer
        TMR0L = 0x18; // Reload value for timing
        
        // 1. Turn OFF all Digits (to prevent ghosting)
        LATA &= 0xE1; 
        
        // 2. Set Segment Data
        int num = display_buffer[digit_scan_index];
        unsigned char pattern = SEG_MAP[num];
        
        // Output Segments A-F on PORTC (RC0-RC5)
        // Mask: Maintain RC6/RC7 (UART), update RC0-RC5
        LATC = (LATC & 0xC0) | (pattern & 0x3F); 
        
        // Output Segment G on RB2
        // Extract 7th bit (0x40) from pattern
        SEG_G = (pattern >> 6) & 0x01;           
        
        // 3. Turn ON current Digit
        switch(digit_scan_index) {
            case 0: DIGIT_1 = 1; break;
            case 1: DIGIT_2 = 1; break;
            case 2: DIGIT_3 = 1; break;
            case 3: DIGIT_4 = 1; break;
        }
        
        // Move to next digit
        digit_scan_index++;
        if (digit_scan_index > 3) digit_scan_index = 0;
        
        // Clear Interrupt Flag
        INTCONbits.TMR0IF = 0;
    }
}