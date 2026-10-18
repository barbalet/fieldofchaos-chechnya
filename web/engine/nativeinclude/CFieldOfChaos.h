#ifndef C_FIELD_OF_CHAOS_H
#define C_FIELD_OF_CHAOS_H
// Native interface to the same skirmish engine compiled by web/build.sh.
unsigned long save_ptr(void);
int save_size(void);
void restore_meta(int side,int round);
int unit_count(void);
int patrol_size(void);
int unit_skill(int unit,int skill);
int rounds_required(int unit);
int ammunition_exhausted(void);
int run_range_inches(int unit);
int can_run(int unit,int x,int y);
int run_unit(int unit,int x,int y);
int can_focus_attack(int unit,int target);
int focused_attack(int unit,int target);
void start(unsigned int seed);
int state(int unit, int key);
int terrain(int x, int y);
int alive(int unit);
int movement_range_inches(int unit);
int can_move(int unit, int x, int y);
int move_unit(int unit, int x, int y);
int can_attack(int unit, int target);
int attack(int unit, int target);
int reload(int unit);
int heal(int unit, int target);
int end_turn(void);
#endif
