/**
 * @file display.h
 * @brief Header file for 7-Segment Display and LED control.
 */

#ifndef DISPLAY_H
#define DISPLAY_H

/**
 * @brief Initializes IO pins for Display and LEDs.
 * Configures Timer0 for multiplexing.
 */
void Display_Init(void);

/**
 * @brief Updates the score buffer to be shown on the 7-segment display.
 * @param number The score to display (0-9999).
 */
void Display_Update_Score(int number);

/**
 * @brief Controls the status LEDs based on game state.
 * @param color 'G' (Green), 'P' (Yellow/Pause), 'E' (Red/End), 'X' (Off).
 */
void Display_Set_LED(char color);

/**
 * @brief Timer0 Interrupt Handler for display multiplexing.
 * Should be called inside the high-priority ISR.
 */
void Display_ISR_Handler(void);

#endif