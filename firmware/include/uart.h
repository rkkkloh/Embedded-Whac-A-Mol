/**
 * @file uart.h
 * @brief Header file for UART (Bluetooth) communication.
 */

#ifndef UART_H
#define UART_H

/**
 * @brief Initializes the UART module for 9600 baud rate.
 */
void UART_Init(void);

/**
 * @brief Sends a string over UART.
 * @param text Null-terminated string to send.
 */
void UART_Write_Text(char *text);

/**
 * @brief UART Receive Interrupt Handler.
 * Processes incoming commands from Python.
 */
void UART_ISR_Handler(void);

#endif