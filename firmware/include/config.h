/**
 * @file config.h
 * @brief System configuration and hardware pin definitions.
 * @details Defines CPU frequency, Pin mappings for LEDs, Buttons, and 7-Segment display.
 */

#ifndef CONFIG_H
#define CONFIG_H

#include <xc.h>

// --- System Config ---
// Internal Oscillator Frequency (4MHz)
// Used by __delay_ms() and baud rate calculations.
#define _XTAL_FREQ 4000000 

// Threshold for Potentiometer (ADC) changes to reduce noise
#define POT_THRESHOLD 30

// --- Pin Definitions ---

// Status LEDs (Active High)
#define LED_GREEN   LATBbits.LATB3  // Game Start
#define LED_YELLOW  LATBbits.LATB4  // Pause
#define LED_RED     LATBbits.LATB5  // Stop / Menu

// 7-Segment Display - Segment G
// Moved to RB2 because RC7 is occupied by UART (Bluetooth)
#define SEG_G       LATBbits.LATB2

// 7-Segment Digit Selects (Active High for Common Anode via Transistor, or direct logic)
#define DIGIT_1     LATAbits.LATA1
#define DIGIT_2     LATAbits.LATA2
#define DIGIT_3     LATAbits.LATA3
#define DIGIT_4     LATAbits.LATA4

// Control Buttons
#define BTN_CONFIRM PORTBbits.RB0   // Confirm / Pause Button (Interrupt)
#define BTN_8       PORTEbits.RE0   // The 9th Game Button (Mole Input)

#endif // CONFIG_H