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

static void sound_finish(uint8_t interrupt_state)
{
    sound_init();
    /*
     * The classic z88dk ZX beeper opens sound twice: once in bit_beep_callee
     * and once in the target ROM wrapper.  The nested open overwrites the
     * saved IFF state, so the matching closes can leave interrupts disabled.
     * Preserve the caller's real state around the complete effect.
     */
    z80_set_int_state(interrupt_state);
}

/* An original, short rising three-note pickup: coin-like, not a copied tune. */
void sound_hit(void)
{
    uint8_t interrupt_state = z80_get_int_state();

    bit_beep(35, 180);
    bit_beep(50, 112);
    bit_beep(70, 72);
    sound_finish(interrupt_state);
}

void sound_miss(void)
{
    uint8_t interrupt_state = z80_get_int_state();

    bit_beep(50, 100);
    bit_beep(65, 175);
    bit_beep(80, 280);
    sound_finish(interrupt_state);
}

void sound_repeat(void)
{
    uint8_t interrupt_state = z80_get_int_state();

    bit_beep(30, 58);
    sound_finish(interrupt_state);
}
