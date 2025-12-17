/**
 * @file inputs.h
 * @brief Header file for Input handling (Buttons & ADC).
 */

#ifndef INPUTS_H
#define INPUTS_H

/**
 * @brief Initializes Input pins, ADC module, and External Interrupt (INT0).
 */
void Inputs_Init(void);

/**
 * @brief Reads the Potentiometer value.
 * @return 10-bit ADC value (0-1023).
 */
int ADC_Read(void);

/**
 * @brief Scans the game button matrix (0-8) and sends UART commands if pressed.
 * Handles debouncing and state tracking.
 */
void Check_Matrix_Buttons(void);

/**
 * @brief Interrupt Handler for the Confirm Button (INT0).
 * Should be called inside the high-priority ISR.
 */
void Inputs_ISR_Handler(void);

// Flag indicating if the Confirm button was pressed (set in ISR)
extern volatile int btn_confirm_flag;

#endif