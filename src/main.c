#include <arch/z80.h>
#include <conio.h>
#include <stdint.h>

#include "dictionary_meta.h"
#include "game.h"
#include "locale.h"
#include "license.h"
#include "screen.h"
#include "game_sound.h"

#define UI_NORMAL ZX_ATTR(ZX_INK_WHITE, ZX_INK_BLACK, 0u)
#define UI_BRIGHT ZX_ATTR(ZX_INK_WHITE, ZX_INK_BLACK, 1u)
#define UI_ACCENT ZX_ATTR(ZX_INK_CYAN, ZX_INK_BLACK, 1u)
#define UI_GOOD ZX_ATTR(ZX_INK_GREEN, ZX_INK_BLACK, 1u)
#define UI_BAD ZX_ATTR(ZX_INK_RED, ZX_INK_BLACK, 1u)
#define UI_WARN ZX_ATTR(ZX_INK_YELLOW, ZX_INK_BLACK, 1u)

/* These markers are also read by the emulator smoke test. */
volatile uint8_t zx_boot_stage;
volatile uint8_t zx_selected_word_length;
volatile uint8_t zx_render_count;
volatile uint8_t zx_last_redraw_rows;
volatile uint8_t zx_full_render_count;
volatile uint8_t zx_last_sound;
volatile uint8_t zx_known_hit_letter;
volatile uint8_t zx_known_miss_letter;

static uint8_t wait_key(void)
{
    uint8_t key;

    do {
        key = (uint8_t)getk();
        random_tick();
    } while (key == 0u);

    while (getk() != 0)
        random_tick();

    if (key >= 'a' && key <= 'z')
        key = (uint8_t)(key - 'a' + 'A');
    return key;
}

static uint8_t append_text(char *target, uint8_t position, const char *text)
{
    while (*text && position < 31u)
        target[position++] = *text++;
    target[position] = '\0';
    return position;
}

static uint8_t append_number(char *target, uint8_t position, uint16_t value)
{
    char digits[5];
    uint8_t count = 0u;

    do {
        digits[count++] = (char)('0' + value % 10u);
        value /= 10u;
    } while (value != 0u && count < 5u);

    while (count != 0u && position < 31u)
        target[position++] = digits[--count];
    target[position] = '\0';
    return position;
}

static const char *mode_name(uint8_t mode)
{
    if (mode == 1u)
        return TXT_MODE_SHORT;
    if (mode == 2u)
        return TXT_MODE_MEDIUM;
    if (mode == 3u)
        return TXT_MODE_LONG;
    return TXT_MODE_ALL;
}

static uint8_t find_miss_letter(const GameState *game)
{
    uint8_t letter;

    for (letter = 'A'; letter <= 'Z'; ++letter) {
        uint8_t position;
        uint8_t found = 0u;

        for (position = 0u; position < game->length; ++position) {
            if (game->word[position] == (char)(letter - 'A' + 'a')) {
                found = 1u;
                break;
            }
        }
        if (!found)
            return letter;
    }
    return 'Z';
}

static void draw_stat(uint8_t row, const char *label, uint16_t value)
{
    char line[32];
    uint8_t position = 0u;

    position = append_text(line, position, label);
    append_number(line, position, value);
    screen_clear_cells(17u, row, 15u, UI_NORMAL);
    screen_text(17u, row, line, UI_NORMAL);
}

static void render_errors(const GameState *game)
{
    char line[16];
    uint8_t position;

    position = append_text(line, 0u, TXT_ERRORS_LABEL);
    position = append_number(line, position, game->errors);
    position = append_text(line, position, "/");
    append_number(line, position, MAX_ERRORS);
    screen_clear_cells(17u, 7u, 15u, UI_NORMAL);
    screen_text(17u, 7u, line, game->errors >= 5u ? UI_BAD : UI_NORMAL);
}

static void render_message(const char *message, uint8_t attr)
{
    screen_clear_text_row(23u, UI_NORMAL);
    screen_text_center(23u, message, attr);
}

static void render_word(const GameState *game, uint8_t reveal)
{
    char display[32];
    uint8_t source;
    uint8_t target = 0u;

    for (source = 0u; source < game->length; ++source) {
        char upper = (char)(game->word[source] - 'a' + 'A');
        display[target++] = reveal || game_letter_known(game, upper) ? upper : '_';
        if (source + 1u < game->length)
            display[target++] = ' ';
    }
    display[target] = '\0';
    screen_clear_text_row(18u, UI_NORMAL);
    screen_text_center(18u, display, UI_BRIGHT);
}

static void render_alphabet(const GameState *game)
{
    uint8_t i;

    for (i = 0u; i < 26u; ++i) {
        char letter = (char)('A' + i);
        uint8_t row = i < 13u ? 20u : 21u;
        uint8_t column = (uint8_t)(3u + ((i % 13u) << 1));
        uint8_t attr = game_letter_known(game, letter) ? UI_BAD : UI_ACCENT;

        screen_char(column, row, letter, attr);
    }
}

static void render_alphabet_letter(uint8_t key)
{
    uint8_t index = (uint8_t)(key - 'A');
    uint8_t row = index < 13u ? 20u : 21u;
    uint8_t column = (uint8_t)(3u + ((index % 13u) << 1));

    screen_char(column, row, (char)key, UI_BAD);
}

static void render_game_full(const GameState *game, const char *message,
                             uint8_t reveal)
{
    screen_clear(UI_NORMAL);
#ifdef ZX48
    screen_text_center(0u, TXT_TITLE_48, UI_ACCENT);
#else
    screen_text_center(0u, TXT_TITLE_128, UI_ACCENT);
#endif
    screen_text_center(1u, TXT_EDITION, UI_NORMAL);
    screen_draw_gallows(game->errors);

    screen_text(17u, 4u, TXT_MODE_LABEL, UI_WARN);
    screen_text(17u, 5u, mode_name(game->mode), UI_BRIGHT);
    render_errors(game);
    draw_stat(9u, TXT_ROUND_LABEL, (uint16_t)(game->rounds + 1u));
    draw_stat(10u, TXT_WINS_LABEL, game->wins);
    draw_stat(12u, TXT_DICTIONARY_LABEL, dictionary_count());

    screen_text_center(17u, TXT_GUESS_WORD, UI_WARN);
    render_word(game, reveal);
    render_alphabet(game);
    render_message(message, UI_NORMAL);
    zx_last_redraw_rows = 24u;
    ++zx_full_render_count;
    ++zx_render_count;
}

static void update_after_guess(const GameState *game, uint8_t key, uint8_t result)
{
    if (result == 0u) {
        sound_repeat();
        zx_last_sound = 1u;
        render_message(TXT_LETTER_REPEAT, UI_WARN);
        zx_last_redraw_rows = 1u;
    } else if (result == 1u) {
        sound_miss();
        zx_last_sound = 2u;
        screen_draw_error_part(game->errors);
        render_errors(game);
        render_alphabet_letter(key);
        render_message(TXT_LETTER_MISS, UI_BAD);
        zx_last_redraw_rows = 4u;
    } else {
        sound_hit();
        zx_last_sound = 3u;
        render_word(game, 0u);
        render_alphabet_letter(key);
        render_message(TXT_LETTER_HIT, UI_GOOD);
        zx_last_redraw_rows = 3u;
    }
    ++zx_render_count;
}

static uint8_t choose_mode(void)
{
    char line[32];
    uint8_t position;
    uint8_t key;

    for (;;) {
        zx_boot_stage = 0x4du;
        screen_clear(UI_NORMAL);
#ifdef ZX48
        screen_text_center(2u, TXT_TITLE_48, UI_ACCENT);
#else
        screen_text_center(2u, TXT_TITLE_128, UI_ACCENT);
#endif
        screen_text_center(4u, TXT_ASCII_NOTICE, UI_NORMAL);

        position = append_text(line, 0u, TXT_DICTIONARY_PREFIX);
        position = append_number(line, position, dictionary_count());
        append_text(line, position, TXT_DICTIONARY_SUFFIX);
        screen_text_center(6u, line, UI_WARN);

        screen_text(6u, 9u, TXT_MODE_SHORT_LINE, UI_BRIGHT);
        screen_text(6u, 11u, TXT_MODE_MEDIUM_LINE, UI_BRIGHT);
        screen_text(6u, 13u, TXT_MODE_LONG_LINE, UI_BRIGHT);
        screen_text(6u, 15u, TXT_MODE_ALL_LINE, UI_BRIGHT);
        screen_text_center(19u, TXT_CHOOSE_MODE, UI_ACCENT);
        screen_text_center(21u, TXT_KEYBOARD, UI_NORMAL);
        screen_text_center(23u, TXT_LICENSE_KEY, UI_WARN);

        key = wait_key();
        if (key >= '1' && key <= '4')
            return (uint8_t)(key - '0');
        if (key == 'L')
            license_show();
    }
}

static uint8_t finish_round(GameState *game, uint8_t won)
{
    char message[32];
    uint8_t position;
    uint8_t key;

    ++game->rounds;
    game->error_total = (uint16_t)(game->error_total + game->errors);
    if (won)
        ++game->wins;

    render_word(game, 1u);
    draw_stat(9u, TXT_ROUND_LABEL, game->rounds);
    draw_stat(10u, TXT_WINS_LABEL, game->wins);
    if (won) {
        render_message(TXT_WON, UI_GOOD);
    } else {
        position = append_text(message, 0u, TXT_WORD_PREFIX);
        position = append_text(message, position, game->word);
        message[position] = '\0';
        render_message(message, UI_BAD);
    }

    screen_clear_text_row(22u, UI_NORMAL);
    screen_text_center(22u, TXT_NEXT_PROMPT, UI_WARN);
    zx_last_redraw_rows = 5u;
    ++zx_render_count;

    for (;;) {
        key = wait_key();
        if (key == 13u || key == 10u)
            return 0u;
        if (key == 'M')
            return 1u;
        if (key == 'Q')
            return 2u;
    }
}

int main(void)
{
    GameState game;
    uint8_t mode = 2u;
    uint8_t action = 1u;

    sound_init();
    game_init(&game);

    while (action != 2u) {
        uint8_t result;
        uint8_t key;

        if (action == 1u)
            mode = choose_mode();
        game_new_round(&game, mode);
        zx_selected_word_length = game.length;
        zx_known_hit_letter = (uint8_t)(game.word[0] - 'a' + 'A');
        zx_known_miss_letter = find_miss_letter(&game);
        zx_boot_stage = 0x47u;
        render_game_full(&game, TXT_TYPE_LETTER, 0u);

        while (!game_won(&game) && !game_lost(&game)) {
            do {
                key = wait_key();
            } while (key < 'A' || key > 'Z');

            result = game_guess(&game, (char)key);
            update_after_guess(&game, key, result);
        }
        action = finish_round(&game, game_won(&game));
    }

    screen_clear(UI_NORMAL);
    screen_text_center(9u, TXT_THANKS, UI_ACCENT);
    screen_text_center(12u, TXT_ANY_KEY, UI_NORMAL);
    wait_key();
    return 0;
}
