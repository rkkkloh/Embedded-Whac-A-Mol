#ifndef DISPLAY_H
#define DISPLAY_H

void Display_Init(void);
void Display_Update_Score(int number);
void Display_Set_LED(char color); // 'G', 'P', 'E', 'X'
void Display_ISR_Handler(void);   // Call this inside ISR

#endif