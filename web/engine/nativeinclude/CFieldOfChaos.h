#ifndef C_FIELD_OF_CHAOS_H
#define C_FIELD_OF_CHAOS_H
// Native interface to the same skirmish engine compiled by web/build.sh.
void start(unsigned int seed);
int state(int unit, int key);
int terrain(int x, int y);
int alive(int unit);
int can_move(int unit, int x, int y);
int move_unit(int unit, int x, int y);
int can_attack(int unit, int target);
int attack(int unit, int target);
int reload(int unit);
int heal(int unit, int target);
int end_turn(void);
#endif
