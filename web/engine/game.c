#include "fieldofchaosgold.h"
#include <string.h>
typedef struct {focgold_character c; int x,y,moved,acted,jam,pace,focused;} Unit;
static Unit units[10];
static int side,round_no,winner,last_roll,last_threshold,last_location,last_hit,last_dice,last_bonus;
int movement_range_inches(int i);
int terrain(int x,int y){if(x<0||y<0||x>=24||y>=16)return 2;
 if((x==8&&y>=2&&y<=6)||(x==15&&y>=9&&y<=13)||(y==8&&x>=10&&x<=13))return 2;
 if((x>=5&&x<=6&&y>=9&&y<=11)||(x>=17&&x<=18&&y>=4&&y<=6)||(x==11&&y>=3&&y<=5)||(x==12&&y>=11&&y<=13))return 1;return 0;}
int alive(int i){return i>=0&&i<10&&!focgold_is_unconscious(&units[i].c.current_wounds)&&!focgold_is_dead(&units[i].c.current_wounds);}
static int valid(int i){return winner<0&&alive(i)&&i/5==side;}
static void check(void){int a=0,b=0;for(int i=0;i<10;i++)if(alive(i)){if(i<5)a++;else b++;}if(!a)winner=1;if(!b)winner=0;}
int unit_count(void) { return 10; }
int patrol_size(void) { return 5; }
int unit_skill(int i,int skill) {
    if(i<0 || i>=10) return 0;
    if(skill==17) return i%5==4; /* Scenario-specific Sniper Training. */
    return focgold_skill_value(&units[i].c.skills,(focgold_skill_id)skill);
}
int rounds_required(int i) {
    if(i<0 || i>=10) return 0;
    return focgold_weapon_shots_per_turn(units[i].c.weapon,units[i].c.skills.firearm_advanced!=0);
}
int ammunition_exhausted(void) {
    if(winner>=0) return 0;
    for(int i=0;i<10;i++) if(alive(i) &&
        (units[i].c.rounds_in_clip>=rounds_required(i) || units[i].c.clips>0)) return 0;
    return 1;
}
void start(unsigned int seed) {
    memset(units,0,sizeof(units)); focgold_seed(seed);
    side=0; round_no=1; winner=-1; last_hit=last_dice=last_bonus=0;
    for(int i=0;i<10;i++) {
        Unit *u=&units[i]; int role=i%5;
        u->x=i<5?2:21; u->y=1+role*3;
        u->c.weapon=role==0?focgold_weapon_rifle:role==3?focgold_weapon_submg:
                    role==4?focgold_weapon_sniper_rifle:focgold_weapon_carbine;
        u->c.skills.firearm_basic=1;
        u->c.skills.firearm_advanced=role==0 || role==3 || role==4;
        u->c.skills.running=role==1 || role==3;
        u->c.skills.first_aid=role==2;
        u->c.skills.paramedic=role==2;
        u->c.skills.close_combat=role!=4;
        u->c.clips=3; u->c.rounds_in_clip=10; u->c.has_bandage=true;
        focgold_default_wounds(&u->c.maximum_wounds);
        u->c.current_wounds=u->c.maximum_wounds;
    }
}
int state(int i,int key){if(key==20)return side;if(key==21)return round_no;if(key==22)return winner;if(key==23)return last_roll;if(key==24)return last_threshold;if(key==25)return last_location;if(key==26)return last_hit;if(key==30)return last_dice;if(key==31)return last_bonus;if(i<0||i>=10)return -1;Unit *u=&units[i];switch(key){case 0:return u->x;case 1:return u->y;case 2:return alive(i);case 3:return u->moved;case 4:return u->acted;case 5:return u->c.rounds_in_clip;case 6:return u->c.clips;case 7:return u->jam;case 8:return focgold_total_wounds(&u->c.current_wounds);case 9:return u->c.weapon;case 10:return movement_range_inches(i)/2;case 27:return u->pace;case 28:return u->focused;case 29:return rounds_required(i);default:if(key>=11&&key<=17)return focgold_wound_value(&u->c.current_wounds,key-11);}return -1;}
static int absval(int v){return v<0?-v:v;}
static int occupied(int x,int y){for(int i=0;i<10;i++)if(alive(i)&&units[i].x==x&&units[i].y==y)return 1;return 0;}
/* Gameplay movement radii: at least four cells for every healthy unit.
 * Keep the Gold tabletop rules unchanged; this scale is for the grid game. */
int movement_range_inches(int i) {
    if (!alive(i)) return 0;
    focgold_wounds healthy;
    focgold_default_wounds(&healthy);
    int normal=focgold_movement_inches(focgold_weapon_movement_rule(units[i].c.weapon),
                                      &units[i].c.skills, &healthy);
    int inches=normal*2;
    if(inches<8) inches=8;
    if(inches>12) inches=12;
    int disabled=(units[i].c.current_wounds.left_leg<=0)+
                 (units[i].c.current_wounds.right_leg<=0);
    return disabled==2?0:disabled==1?inches/2:inches;
}
static int movement_clear(int x, int y) {
    return terrain(x, y) != 2 && !occupied(x, y);
}
/* Supercover of the straight centre-to-centre segment. At an exact corner,
 * both adjacent squares must be clear, so units cannot squeeze through ruins. */
static int movement_line_clear(int x, int y, int tx, int ty) {
    int nx=absval(tx-x), ny=absval(ty-y), ix=0, iy=0;
    int sx=tx>x?1:-1, sy=ty>y?1:-1;
    while(ix<nx || iy<ny) {
        int crossing_x=(1+2*ix)*ny, crossing_y=(1+2*iy)*nx;
        if(crossing_x==crossing_y) {
            if(!movement_clear(x+sx,y) || !movement_clear(x,y+sy)) return 0;
            x+=sx; y+=sy; ix++; iy++;
        } else if(crossing_x<crossing_y) { x+=sx; ix++; }
        else { y+=sy; iy++; }
        if(!movement_clear(x,y)) return 0;
    }
    return 1;
}
static int can_travel(int i,int x,int y,int inches) {
    if(!valid(i) || units[i].moved || !movement_clear(x,y)) return 0;
    int dx=x-units[i].x, dy=y-units[i].y;
    if(4*(dx*dx+dy*dy)>inches*inches) return 0;
    return movement_line_clear(units[i].x,units[i].y,x,y);
}
int can_move(int i,int x,int y) { return can_travel(i,x,y,movement_range_inches(i)); }
int run_range_inches(int i) {
    if(!alive(i)) return 0;
    int normal=movement_range_inches(i);
    return units[i].c.skills.running?normal*2:normal*3/2;
}
int can_run(int i,int x,int y) { return valid(i) && !units[i].acted && can_travel(i,x,y,run_range_inches(i)); }
int move_unit(int i,int x,int y) {
    if(!can_move(i,x,y)) return 0;
    units[i].x=x; units[i].y=y; units[i].moved=1; units[i].pace=1; return 1;
}
int run_unit(int i,int x,int y) {
    if(!can_run(i,x,y)) return 0;
    units[i].x=x; units[i].y=y; units[i].moved=units[i].acted=1; units[i].pace=2; return 1;
}
static int distance(int i,int j){int x=absval(units[i].x-units[j].x),y=absval(units[i].y-units[j].y);return 2*(x>y?x:y);}
int sight(int i,int j){int x=units[i].x,y=units[i].y,tx=units[j].x,ty=units[j].y,dx=absval(tx-x),dy=-absval(ty-y),sx=x<tx?1:-1,sy=y<ty?1:-1,e=dx+dy;while(x!=tx||y!=ty){int e2=2*e;if(e2>=dy){e+=dy;x+=sx;}if(e2<=dx){e+=dx;y+=sy;}if(terrain(x,y)==2)return 0;}return 1;}
int can_attack(int i,int j){return valid(i)&&alive(j)&&i/5!=j/5&&!units[i].acted&&!units[i].jam&&units[i].c.rounds_in_clip>=rounds_required(i)&&focgold_can_firearm(&units[i].c.current_wounds)&&focgold_weapon_can_fire_at_distance(units[i].c.weapon,distance(i,j))&&sight(i,j);}
int can_focus_attack(int i,int j) { return can_attack(i,j) && !units[i].moved; }
static int resolve_attack(int i,int j,int focus) {
    if(!(focus?can_focus_attack(i,j):can_attack(i,j))) return 0;
    int d=distance(i,j),band=0;
    while(band<2 && d>focgold_weapon_range_inches(units[i].c.weapon,band)) band++;
    focgold_attack_modifiers mods={0};
    mods.cover=terrain(units[j].x,units[j].y)?focgold_cover_light:focgold_cover_none;
    mods.target_movement=units[j].pace==2?focgold_target_movement_fast:
                         units[j].pace==1?focgold_target_movement_standard:focgold_target_movement_none;
    focgold_attack_result r;
    focgold_resolve_ranged_attack(&units[i].c,&units[j].c,band,&mods,0,&r);
    last_bonus=focus?(1+unit_skill(i,17)):0;
    for(int k=0;k<last_bonus;k++) { r.dice_total+=focgold_roll_d6(); r.dice_count++; }
    if(!r.hit && r.dice_total>=r.required_to_hit) {
        r.hit=true; r.location=focgold_roll_bullet_hit_location(); r.wounds_inflicted=1;
    }
    focgold_apply_ranged_attack_ammo(&units[i].c,&r);
    units[i].jam=r.jammed; units[i].acted=1; units[i].focused=focus;
    if(focus) units[i].moved=1;
    last_roll=r.dice_total; last_threshold=r.required_to_hit; last_location=r.location;
    last_hit=r.hit; last_dice=r.dice_count;
    if(r.hit) focgold_apply_wounds(&units[j].c.current_wounds,r.location,r.wounds_inflicted);
    check(); return 1;
}
int attack(int i,int j) { return resolve_attack(i,j,0); }
int focused_attack(int i,int j) { return resolve_attack(i,j,1); }
int reload(int i){if(!valid(i)||units[i].acted)return 0;if(units[i].jam){units[i].jam=0;}else if(!focgold_reload_character(&units[i].c))return 0;units[i].acted=1;return 1;}
int heal(int i,int j){if(!valid(i)||!alive(j)||i/5!=j/5||units[i].acted||distance(i,j)>2)return 0;int loc=-1;for(int k=0;k<7;k++)if(focgold_wound_value(&units[j].c.current_wounds,k)<focgold_wound_value(&units[j].c.maximum_wounds,k)){loc=k;break;}if(loc<0)return 0;focgold_healing_result r;focgold_healing_method method=units[i].c.skills.paramedic?focgold_healing_paramedic:units[i].c.skills.first_aid?focgold_healing_first_aid:focgold_healing_bandage;focgold_resolve_healing(&units[i].c,&units[j].c,method,&r);focgold_apply_healing_result_to_location(&units[j].c,&r,loc);units[i].acted=1;last_roll=r.highest_die;last_threshold=r.required_to_recover;last_hit=r.recovered;last_location=loc;return 1;}
int end_turn(void){if(winner>=0)return 0;side=1-side;if(side==0)round_no++;for(int i=0;i<10;i++){units[i].moved=0;units[i].acted=0;units[i].focused=0;if(i/5==side)units[i].pace=0;}return 1;}
unsigned long save_ptr(void){return (unsigned long)units;}
int save_size(void){return sizeof(units);}
void restore_meta(int s,int r){side=s;round_no=r;winner=-1;check();}
