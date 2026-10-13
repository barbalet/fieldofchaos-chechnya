#include "fieldofchaosgold.h"
#include <string.h>
typedef struct {focgold_character c; int x,y,moved,acted,jam;} Unit;
static Unit units[6];
static int side,round_no,winner,last_roll,last_threshold,last_location,last_hit;
int terrain(int x,int y){if(x<0||y<0||x>=24||y>=16)return 2;
 if((x==8&&y>=2&&y<=6)||(x==15&&y>=9&&y<=13)||(y==8&&x>=10&&x<=13))return 2;
 if((x>=5&&x<=6&&y>=9&&y<=11)||(x>=17&&x<=18&&y>=4&&y<=6)||(x==11&&y>=3&&y<=5)||(x==12&&y>=11&&y<=13))return 1;return 0;}
int alive(int i){return i>=0&&i<6&&!focgold_is_unconscious(&units[i].c.current_wounds)&&!focgold_is_dead(&units[i].c.current_wounds);}
static int valid(int i){return winner<0&&alive(i)&&i/3==side;}
static void check(void){int a=0,b=0;for(int i=0;i<6;i++)if(alive(i)){if(i<3)a++;else b++;}if(!a)winner=1;if(!b)winner=0;}
void start(unsigned int seed){memset(units,0,sizeof(units));focgold_seed(seed);side=0;round_no=1;winner=-1;last_hit=0;
 for(int i=0;i<6;i++){Unit *u=&units[i];u->x=i<3?2:21;u->y=3+(i%3)*4;u->c.weapon=i%3==0?focgold_weapon_rifle:focgold_weapon_carbine;u->c.skills.firearm_basic=1;u->c.skills.firearm_advanced=1;u->c.skills.first_aid=1;u->c.skills.close_combat=1;u->c.clips=3;u->c.rounds_in_clip=10;focgold_default_wounds(&u->c.maximum_wounds);u->c.current_wounds=u->c.maximum_wounds;}}
int state(int i,int key){if(key==20)return side;if(key==21)return round_no;if(key==22)return winner;if(key==23)return last_roll;if(key==24)return last_threshold;if(key==25)return last_location;if(key==26)return last_hit;if(i<0||i>=6)return -1;Unit *u=&units[i];switch(key){case 0:return u->x;case 1:return u->y;case 2:return alive(i);case 3:return u->moved;case 4:return u->acted;case 5:return u->c.rounds_in_clip;case 6:return u->c.clips;case 7:return u->jam;case 8:return focgold_total_wounds(&u->c.current_wounds);case 9:return u->c.weapon;case 10:return focgold_movement_inches(focgold_weapon_movement_rule(u->c.weapon),&u->c.skills,&u->c.current_wounds)/2;default:if(key>=11&&key<=17)return focgold_wound_value(&u->c.current_wounds,key-11);}return -1;}
static int absval(int v){return v<0?-v:v;}
static int occupied(int x,int y){for(int i=0;i<6;i++)if(alive(i)&&units[i].x==x&&units[i].y==y)return 1;return 0;}
int can_move(int i,int x,int y){if(!valid(i)||units[i].moved||terrain(x,y)==2||occupied(x,y))return 0;int dist[384],queue[384],head=0,tail=0;for(int n=0;n<384;n++)dist[n]=-1;int p=units[i].y*24+units[i].x;dist[p]=0;queue[tail++]=p;int max=state(i,10);while(head<tail){int q=queue[head++],qx=q%24,qy=q/24;if(qx==x&&qy==y)return 1;if(dist[q]>=max)continue;int dx[]={1,-1,0,0},dy[]={0,0,1,-1};for(int k=0;k<4;k++){int nx=qx+dx[k],ny=qy+dy[k];if(terrain(nx,ny)==2||occupied(nx,ny))continue;int n=ny*24+nx;if(dist[n]<0){dist[n]=dist[q]+1;queue[tail++]=n;}}}return 0;}
int move_unit(int i,int x,int y){if(!can_move(i,x,y))return 0;units[i].x=x;units[i].y=y;units[i].moved=1;return 1;}
static int distance(int i,int j){int x=absval(units[i].x-units[j].x),y=absval(units[i].y-units[j].y);return 2*(x>y?x:y);}
int sight(int i,int j){int x=units[i].x,y=units[i].y,tx=units[j].x,ty=units[j].y,dx=absval(tx-x),dy=-absval(ty-y),sx=x<tx?1:-1,sy=y<ty?1:-1,e=dx+dy;while(x!=tx||y!=ty){int e2=2*e;if(e2>=dy){e+=dy;x+=sx;}if(e2<=dx){e+=dx;y+=sy;}if(terrain(x,y)==2)return 0;}return 1;}
int can_attack(int i,int j){return valid(i)&&alive(j)&&i/3!=j/3&&!units[i].acted&&!units[i].jam&&units[i].c.rounds_in_clip>=2&&focgold_can_firearm(&units[i].c.current_wounds)&&focgold_weapon_can_fire_at_distance(units[i].c.weapon,distance(i,j))&&sight(i,j);}
int attack(int i,int j){if(!can_attack(i,j))return 0;int d=distance(i,j),band=0;while(band<2&&d>focgold_weapon_range_inches(units[i].c.weapon,band))band++;focgold_attack_modifiers mods={0};mods.cover=terrain(units[j].x,units[j].y)?focgold_cover_light:focgold_cover_none;focgold_attack_result r;focgold_resolve_ranged_attack(&units[i].c,&units[j].c,band,&mods,0,&r);focgold_apply_ranged_attack_ammo(&units[i].c,&r);units[i].jam=r.jammed;units[i].acted=1;last_roll=r.dice_total;last_threshold=r.required_to_hit;last_location=r.location;last_hit=r.hit;if(r.hit)focgold_apply_wounds(&units[j].c.current_wounds,r.location,r.wounds_inflicted);check();return 1;}
int reload(int i){if(!valid(i)||units[i].acted)return 0;if(units[i].jam){units[i].jam=0;}else if(!focgold_reload_character(&units[i].c))return 0;units[i].acted=1;return 1;}
int heal(int i,int j){if(!valid(i)||!alive(j)||i/3!=j/3||units[i].acted||distance(i,j)>2)return 0;int loc=-1;for(int k=0;k<7;k++)if(focgold_wound_value(&units[j].c.current_wounds,k)<focgold_wound_value(&units[j].c.maximum_wounds,k)){loc=k;break;}if(loc<0)return 0;focgold_healing_result r;focgold_resolve_healing(&units[i].c,&units[j].c,focgold_healing_first_aid,&r);focgold_apply_healing_result_to_location(&units[j].c,&r,loc);units[i].acted=1;last_roll=r.highest_die;last_threshold=r.required_to_recover;last_hit=r.recovered;last_location=loc;return 1;}
int end_turn(void){if(winner>=0)return 0;side=1-side;if(side==0)round_no++;for(int i=0;i<6;i++){units[i].moved=0;units[i].acted=0;}return 1;}
int save_ptr(void){return (int)(unsigned long)units;}
int save_size(void){return sizeof(units);}
void restore_meta(int s,int r){side=s;round_no=r;winner=-1;check();}
