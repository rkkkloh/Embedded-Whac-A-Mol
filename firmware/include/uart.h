#ifndef UART_H
#define UART_H

void UART_Init(void);
void UART_Write_Text(char *text);
void UART_ISR_Handler(void); // Call inside ISR

#endif