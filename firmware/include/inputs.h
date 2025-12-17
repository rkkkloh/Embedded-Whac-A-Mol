#ifndef INPUTS_H
#define INPUTS_H

void Inputs_Init(void);
int ADC_Read(void);
void Check_Matrix_Buttons(void); // Call in Main Loop
void Inputs_ISR_Handler(void);   // Call inside ISR

extern volatile int btn_confirm_flag;

#endif