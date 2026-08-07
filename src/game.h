#ifndef HANGMAN_GAME_H
#define HANGMAN_GAME_H

#include <stdint.h>
#include "dictionary.h"

#define MAX_ERRORS 7u

typedef struct GameState {
    char word[MAX_WORD_LENGTH + 1u];
    uint32_t guessed;
    uint8_t errors;
    uint8_t length;
    uint8_t mode;
    uint16_t rounds;
    uint16_t wins;
    uint16_t error_total;
} GameState;

void game_init(GameState *game);
void game_new_round(GameState *game, uint8_t mode);
uint8_t game_guess(GameState *game, char letter);
uint8_t game_won(const GameState *game);
uint8_t game_lost(const GameState *game);
uint8_t game_letter_known(const GameState *game, char letter);
uint8_t game_mode_accepts(uint8_t mode, uint8_t length);

void random_tick(void);
uint16_t random_word_index(uint16_t count);

#endif
