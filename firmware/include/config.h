#ifndef CONFIG_H
#define CONFIG_H

#include <xc.h>

// --- System Config ---
#define _XTAL_FREQ 4000000 
#define POT_THRESHOLD 30

// --- Pin Definitions ---
// LEDs
#define LED_GREEN   LATBbits.LATB3
#define LED_YELLOW  LATBbits.LATB4
#define LED_RED     LATBbits.LATB5

// 7-Segment (Segment G on RB2)
#define SEG_G       LATBbits.LATB2

// Digit Selects
#define DIGIT_1     LATAbits.LATA1
#define DIGIT_2     LATAbits.LATA2
#define DIGIT_3     LATAbits.LATA3
#define DIGIT_4     LATAbits.LATA4

// Buttons
#define BTN_CONFIRM PORTBbits.RB0
#define BTN_8       PORTEbits.RE0

#endif