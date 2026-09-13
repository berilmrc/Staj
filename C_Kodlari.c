#include <16f877.h> // Kullanýlacak denetleyicinin baþlýk 
 // dosyasý tanýtýlýyor
#fuses HS, NOWDT, NOPROTECT // Denetleyici konfigürasyon ayarlarý
#use delay(clock=4000000) // Gecikme fonksiyonu için kullanýlan
 // osilatör frekansý belirtiliyor
#use fast_io(b) // Port yönlendirme komutlarý B portu için 
// geçerli
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
 set_tris_b(0x00); // B portunun tüm pinlerini çýkýþ olarak ayarla
 output_b(0x00); // B portunun çýkýþlarýný temizle

 
 for (i=0;i<15;i++)
 {
 output_b(0x0F); // 
 delay_ms(200); // Gecikme
 output_b(0xF0); // 
 delay_ms(200); // Gecikme
 }
 for (i=0;i<5;i++)
 {
output_b(0x55); 
delay_ms(1000); // Gecikme
output_b(0xAA);
delay_ms(1000); // Gecikme
 }
}

