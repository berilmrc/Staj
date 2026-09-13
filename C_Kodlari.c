#include <16f877.h> 
#fuses HS, NOWDT, NOPROTECT 
#use delay(clock=4000000) 
#use fast_io(b)
int i;
void main()
{
 setup_adc_ports(NO_ANALOGS);
 setup_adc(ADC_OFF);
 setup_psp(PSP_DISABLED);
 setup_spi(SPI_SS_DISABLED);
 setup_timer_0(RTCC_INTERNAL|RTCC_DIV_1);
 setup_timer_1(T1_DISABLED);
 setup_timer_2(T2_DISABLED,0,1);
 set_tris_b(0x00);
 output_b(0x00); 
 
 for (i=0;i<15;i++)
 {
 output_b(0x0F);
 delay_ms(200);
 output_b(0xF0);
 delay_ms(200); 
 }
 for (i=0;i<5;i++)
 {
output_b(0x55); 
delay_ms(1000);
output_b(0xAA);
delay_ms(1000);
 }
}

