#include "game.h"

static uint16_t random_state = 0x6d2bu;

static uint8_t text_length(const char *text)
{
    uint8_t length = 0u;

    while (*text++)
        ++length;
    return length;
}

void random_tick(void)
{
    uint16_t value = random_state;

    value ^= (uint16_t)(value << 7);
    value ^= value >> 9;
    value ^= (uint16_t)(value << 8);
    if (value == 0u)
        value = 0x6d2bu;
    random_state = value;
}

uint16_t random_word_index(uint16_t count)
{
    random_tick();
    return random_state % count;
}

void game_init(GameState *game)
{
    uint8_t i;

    for (i = 0u; i <= MAX_WORD_LENGTH; ++i)
        game->word[i] = '\0';
    game->guessed = 0ul;
    game->errors = 0u;
    game->length = 0u;
    game->mode = 2u;
    game->rounds = 0u;
    game->wins = 0u;
    game->error_total = 0u;
}

uint8_t game_mode_accepts(uint8_t mode, uint8_t length)
{
    if (mode == 1u)
        return length >= 3u && length <= 4u;
    if (mode == 2u)
        return length >= 5u && length <= 7u;
    if (mode == 3u)
        return length >= 8u && length <= MAX_WORD_LENGTH;
    return length >= 3u && length <= MAX_WORD_LENGTH;
}

void game_new_round(GameState *game, uint8_t mode)
{
    uint16_t count = dictionary_count();

    game->mode = mode;
    game->guessed = 0ul;
    game->errors = 0u;

    do {
        dictionary_get(random_word_index(count), game->word);
        game->length = text_length(game->word);
    } while (!game_mode_accepts(mode, game->length));
}

uint8_t game_letter_known(const GameState *game, char letter)
{
    uint8_t index = (uint8_t)(letter - 'A');
    return (game->guessed & (1ul << index)) != 0ul;
}

uint8_t game_guess(GameState *game, char letter)
{
    uint8_t i;
    uint8_t hit = 0u;
    uint32_t mask;

    if (letter < 'A' || letter > 'Z')
        return 0u;

    mask = 1ul << (uint8_t)(letter - 'A');
    if ((game->guessed & mask) != 0ul)
        return 0u;

    game->guessed |= mask;
    letter = (char)(letter - 'A' + 'a');
    for (i = 0u; i < game->length; ++i) {
        if (game->word[i] == letter) {
            hit = 1u;
            break;
        }
    }
    if (!hit)
        ++game->errors;
    return hit ? 2u : 1u;
}

uint8_t game_won(const GameState *game)
{
    uint8_t i;

    for (i = 0u; i < game->length; ++i) {
        char upper = (char)(game->word[i] - 'a' + 'A');
        if (!game_letter_known(game, upper))
            return 0u;
    }
    return 1u;
}

uint8_t game_lost(const GameState *game)
{
    return game->errors >= MAX_ERRORS;
}
