#include <sound.h>
#include <arch/z80.h>

#include "game_sound.h"

#define ZX_BORDCR (*(volatile unsigned char *)0x5c48)

void sound_init(void)
{
    /* z88dk's beeper reads the ROM border shadow before every tone. */
    ZX_BORDCR = 0u;
    z80_outp(0x00feu, 0u);
}

/* An original, short rising three-note pickup: coin-like, not a copied tune. */
void sound_hit(void)
{
    bit_beep(35, 180);
    bit_beep(50, 112);
    bit_beep(70, 72);
    sound_init();
}

void sound_miss(void)
{
    bit_beep(50, 100);
    bit_beep(65, 175);
    bit_beep(80, 280);
    sound_init();
}

void sound_repeat(void)
{
    bit_beep(30, 58);
    sound_init();
}
