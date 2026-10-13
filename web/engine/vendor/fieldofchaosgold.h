#ifndef focgold_fieldofchaosgold_h
#define focgold_fieldofchaosgold_h

#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

enum {
    focgold_character_name_capacity = 64,
    focgold_area_max_wounds = 12,
    focgold_standard_clip_rounds = 10,
    focgold_reload_turns = 1,
    focgold_clear_jam_turns = 1,
    focgold_called_head_shot_setup_moves = 2,
    focgold_grenade_reliability_dice = 2,
    focgold_grenade_dud_threshold = 4,
    focgold_grenade_max_throws_stationary = 2
};

typedef enum focgold_stat_id {
    focgold_stat_regular_intelligence = 0,
    focgold_stat_irregular_intelligence,
    focgold_stat_appearance,
    focgold_stat_physical_health,
    focgold_stat_mental_health,
    focgold_stat_count
} focgold_stat_id;

typedef struct focgold_stats {
    int regular_intelligence;
    int irregular_intelligence;
    int appearance;
    int physical_health;
    int mental_health;
} focgold_stats;

typedef enum focgold_skill_id {
    focgold_skill_firearm_basic = 0,
    focgold_skill_firearm_advanced,
    focgold_skill_close_combat,
    focgold_skill_improvised_weapon_basic,
    focgold_skill_clandestine_weapon_basic,
    focgold_skill_carpentry,
    focgold_skill_manufacture_clandestine_weapon,
    focgold_skill_chemistry_basic,
    focgold_skill_explosive_engineering,
    focgold_skill_biology_basic,
    focgold_skill_chemistry_advanced,
    focgold_skill_chemistry_pharmaceutical,
    focgold_skill_first_aid,
    focgold_skill_paramedic,
    focgold_skill_evade,
    focgold_skill_marching,
    focgold_skill_running,
    focgold_skill_count
} focgold_skill_id;

typedef struct focgold_skills {
    int firearm_basic;
    int firearm_advanced;
    int close_combat;
    int improvised_weapon_basic;
    int clandestine_weapon_basic;
    int carpentry;
    int manufacture_clandestine_weapon;
    int chemistry_basic;
    int explosive_engineering;
    int biology_basic;
    int chemistry_advanced;
    int chemistry_pharmaceutical;
    int first_aid;
    int paramedic;
    int evade;
    int marching;
    int running;
} focgold_skills;

typedef enum focgold_weapon {
    focgold_weapon_sniper_rifle = 0,
    focgold_weapon_rifle,
    focgold_weapon_carbine,
    focgold_weapon_automatic,
    focgold_weapon_submg,
    focgold_weapon_shotgun,
    focgold_weapon_count
} focgold_weapon;

typedef enum focgold_range_band {
    focgold_range_close = 0,
    focgold_range_standard,
    focgold_range_long
} focgold_range_band;

typedef enum focgold_shotgun_band {
    focgold_shotgun_near = 0,
    focgold_shotgun_middle,
    focgold_shotgun_far,
    focgold_shotgun_band_count
} focgold_shotgun_band;

typedef enum focgold_grenade_band {
    focgold_grenade_inner = 0,
    focgold_grenade_middle,
    focgold_grenade_outer,
    focgold_grenade_band_count
} focgold_grenade_band;

typedef enum focgold_movement_pace {
    focgold_movement_very_slow = 0,
    focgold_movement_slow,
    focgold_movement_standard,
    focgold_movement_fast
} focgold_movement_pace;

typedef enum focgold_cover {
    focgold_cover_none = 0,
    focgold_cover_light,
    focgold_cover_heavy
} focgold_cover;

typedef enum focgold_target_movement {
    focgold_target_movement_none = 0,
    focgold_target_movement_standard,
    focgold_target_movement_fast
} focgold_target_movement;

typedef enum focgold_foe_type {
    focgold_foe_animal = 0,
    focgold_foe_hunter,
    focgold_foe_soldier
} focgold_foe_type;

typedef enum focgold_damage_source {
    focgold_damage_bullet = 0,
    focgold_damage_shotgun,
    focgold_damage_grenade,
    focgold_damage_melee
} focgold_damage_source;

typedef struct focgold_damage_roll {
    int dice_count;
    int die_sides;
} focgold_damage_roll;

typedef enum focgold_hit_location {
    focgold_hit_left_leg = 0,
    focgold_hit_right_leg,
    focgold_hit_chest,
    focgold_hit_abdomen,
    focgold_hit_left_arm,
    focgold_hit_right_arm,
    focgold_hit_head
} focgold_hit_location;

typedef struct focgold_wounds {
    int head;
    int chest;
    int abdomen;
    int left_arm;
    int right_arm;
    int left_leg;
    int right_leg;
} focgold_wounds;

typedef enum focgold_melee_attack {
    focgold_melee_blow = 0,
    focgold_melee_weapon
} focgold_melee_attack;

typedef enum focgold_healing_method {
    focgold_healing_no_skill = 0,
    focgold_healing_bandage,
    focgold_healing_first_aid,
    focgold_healing_paramedic
} focgold_healing_method;

typedef struct focgold_character {
    char name[focgold_character_name_capacity];
    focgold_stats stats;
    focgold_skills skills;
    focgold_weapon weapon;
    focgold_wounds maximum_wounds;
    focgold_wounds current_wounds;
    int clips;
    int rounds_in_clip;
    bool has_bandage;
} focgold_character;

typedef struct focgold_stat_generation_choice {
    int rolled_dice[3];
    size_t first_inverted_die;
    size_t second_inverted_die;
    size_t plus_two_value;
    size_t stat_value_indices[5];
} focgold_stat_generation_choice;

typedef struct focgold_attack_modifiers {
    focgold_cover cover;
    focgold_target_movement target_movement;
    bool target_has_evade;
    bool line_crosses_grenade_debris;
} focgold_attack_modifiers;

typedef struct focgold_grenade_reliability_result {
    int dice_total;
    bool dud;
} focgold_grenade_reliability_result;

typedef struct focgold_turn_permissions {
    bool can_move;
    bool can_firearm_attack;
    bool can_melee_attack;
    bool can_reload;
    bool can_clear_jam;
    bool can_heal;
    bool can_progress_called_head_shot;
} focgold_turn_permissions;

typedef struct focgold_attack_result {
    bool can_attack;
    bool hit;
    bool head_shot;
    bool jammed;
    bool head_shot_allowed;
    int dice_count;
    int dice_total;
    int skill_dice;
    int modifier_dice;
    int required_to_hit;
    int required_head_shot;
    int shots_fired;
    int rounds_spent;
    focgold_hit_location location;
    int wounds_inflicted;
} focgold_attack_result;

typedef struct focgold_melee_result {
    bool hit;
    int dice_count;
    int skill_dice;
    int dice_total;
    int required_to_hit;
    focgold_hit_location location;
    int wounds_inflicted;
} focgold_melee_result;

typedef struct focgold_healing_result {
    bool recovered;
    int dice_count;
    int highest_die;
    int required_to_recover;
    focgold_hit_location location;
    int wounds_recovered;
} focgold_healing_result;

typedef struct focgold_area_target {
    int id;
    bool ally;
    int distance_inches;
    int lateral_inches;
} focgold_area_target;

typedef struct focgold_area_damage {
    int id;
    bool ally;
    bool affected;
    int wounds_inflicted;
    focgold_hit_location hit_locations[focgold_area_max_wounds];
    focgold_shotgun_band shotgun_band;
    focgold_grenade_band grenade_band;
} focgold_area_damage;

void focgold_seed(unsigned int seed);
int focgold_roll_d6(void);
int focgold_roll_damage(focgold_damage_roll roll);

int focgold_stat_total(const focgold_stats *stats);
int focgold_stat_value(const focgold_stats *stats, focgold_stat_id stat);
bool focgold_validate_initial_stats(const focgold_stats *stats);
bool focgold_validate_long_term_stats(const focgold_stats *stats);
bool focgold_generate_stats(const focgold_stat_generation_choice *choice,
                            focgold_stats *stats);

const char *focgold_stat_name(focgold_stat_id stat);
bool focgold_validate_skills(const focgold_skills *skills);
int focgold_skill_value(const focgold_skills *skills, focgold_skill_id skill);
const char *focgold_skill_name(focgold_skill_id skill);
focgold_stat_id focgold_skill_stat(focgold_skill_id skill);
const focgold_skill_id *focgold_skill_prerequisites(focgold_skill_id skill,
                                                    size_t *count);
bool focgold_skill_improves_healing(focgold_skill_id skill);
size_t focgold_skill_count_for_stat(const focgold_skills *skills,
                                    focgold_stat_id stat);
bool focgold_validate_skill_prerequisites(const focgold_skills *skills);
bool focgold_validate_character_skills(const focgold_character *character);

const char *focgold_weapon_name(focgold_weapon weapon);
bool focgold_parse_weapon(const char *name, focgold_weapon *weapon);
bool focgold_weapon_uses_firearm_basic(focgold_weapon weapon);
int focgold_weapon_range_inches(focgold_weapon weapon,
                                focgold_range_band range);
int focgold_weapon_shots_per_turn(focgold_weapon weapon,
                                  bool has_firearm_advanced);
focgold_movement_pace focgold_weapon_movement_rule(focgold_weapon weapon);
bool focgold_weapon_has_referee_movement_rule(focgold_weapon weapon);
int focgold_weapon_minimum_range_inches(focgold_weapon weapon);
bool focgold_weapon_can_fire_at_distance(focgold_weapon weapon,
                                         int distance_inches);
bool focgold_weapon_can_head_shot(focgold_weapon weapon);
int focgold_weapon_jam_dice_count(focgold_weapon weapon);
int focgold_weapon_jam_threshold(focgold_weapon weapon);
bool focgold_resolve_weapon_jam(focgold_weapon weapon, bool *jammed);
int focgold_reload_turn_count(void);
int focgold_clear_jam_turn_count(void);
bool focgold_apply_ranged_attack_ammo(focgold_character *attacker,
                                      const focgold_attack_result *result);
bool focgold_reload_character(focgold_character *character);
bool focgold_clear_jam_state(bool *jammed);

int focgold_shotgun_total_length_inches(void);
int focgold_shotgun_band_max_inches(focgold_shotgun_band band);
int focgold_shotgun_band_width_inches(focgold_shotgun_band band);
focgold_damage_roll focgold_shotgun_band_wounds(focgold_shotgun_band band);
bool focgold_shotgun_band_for_target(int distance_inches,
                                     int lateral_inches,
                                     focgold_shotgun_band *band);
bool focgold_resolve_shotgun_area(const focgold_area_target *targets,
                                  size_t target_count,
                                  focgold_area_damage *results,
                                  size_t result_count,
                                  size_t *affected_count);

int focgold_grenade_throw_range_inches(void);
int focgold_grenade_radius_inches(focgold_grenade_band band,
                                  bool inside_building);
focgold_damage_roll focgold_grenade_band_wounds(focgold_grenade_band band);
bool focgold_grenade_uses_skill(void);
bool focgold_grenade_skill_modifies_reliability(focgold_skill_id skill);
bool focgold_resolve_grenade_reliability(focgold_grenade_reliability_result *result);
bool focgold_grenade_band_for_distance(int distance_inches,
                                       bool inside_building,
                                       focgold_grenade_band *band);
bool focgold_resolve_grenade_area(const focgold_area_target *targets,
                                  size_t target_count,
                                  bool inside_building,
                                  bool dud,
                                  focgold_area_damage *results,
                                  size_t result_count,
                                  size_t *affected_count);

const char *focgold_range_name(focgold_range_band range);
int focgold_ranged_base_dice(focgold_range_band range);
int focgold_ranged_skill_dice(const focgold_skills *skills);
int focgold_ranged_hit_threshold(focgold_range_band range);
int focgold_ranged_head_shot_threshold(focgold_range_band range);
int focgold_ranged_modifier_dice(const focgold_attack_modifiers *modifiers);

int focgold_called_head_shot_required_setup_moves(void);
bool focgold_called_head_shot_ready(int moves_declared_before_firing);
bool focgold_called_head_shot_miss_is_total_miss(void);
int focgold_called_head_shot_progress_after_turn(int moves_declared_before_firing,
                                                 bool spent_setup_move);

int focgold_movement_inches(focgold_movement_pace pace,
                            const focgold_skills *skills,
                            const focgold_wounds *wounds);
int focgold_movement_after_one_grenade_inches(focgold_movement_pace pace,
                                              const focgold_skills *skills,
                                              const focgold_wounds *wounds);
bool focgold_can_throw_two_grenades(bool stationary);
focgold_turn_permissions focgold_two_grenade_turn_permissions(void);

void focgold_default_wounds(focgold_wounds *wounds);
int focgold_total_wounds(const focgold_wounds *wounds);
int focgold_wound_value(const focgold_wounds *wounds,
                        focgold_hit_location location);
bool focgold_apply_wounds(focgold_wounds *wounds,
                          focgold_hit_location location,
                          int wounds_inflicted);
bool focgold_apply_area_damage_to_wounds(focgold_wounds *wounds,
                                         const focgold_area_damage *damage);
bool focgold_recover_wound(focgold_wounds *current,
                           const focgold_wounds *maximum,
                           focgold_hit_location location);
bool focgold_apply_healing_result(focgold_character *target,
                                  const focgold_healing_result *result);
bool focgold_apply_healing_result_to_location(focgold_character *target,
                                              const focgold_healing_result *result,
                                              focgold_hit_location location);
bool focgold_is_unconscious(const focgold_wounds *wounds);
bool focgold_is_grave_condition(const focgold_wounds *wounds);
bool focgold_is_dead(const focgold_wounds *wounds);
bool focgold_can_firearm(const focgold_wounds *wounds);
focgold_hit_location focgold_hit_location_for_3d6_total(int total);
focgold_hit_location focgold_roll_bullet_hit_location(void);
focgold_hit_location focgold_roll_blast_hit_location(void);
const char *focgold_hit_location_name(focgold_hit_location location);

int focgold_melee_base_dice(focgold_melee_attack attack);
int focgold_melee_hit_threshold(focgold_melee_attack attack);
bool focgold_melee_skill_applies(focgold_melee_attack attack,
                                 focgold_skill_id skill);
int focgold_melee_skill_dice(const focgold_skills *skills,
                             focgold_melee_attack attack);
int focgold_melee_skill_modifier_dice(const focgold_skills *skills,
                                      focgold_melee_attack attack);

int focgold_healing_dice_count(focgold_healing_method method);
int focgold_healing_required_to_recover(focgold_healing_method method);
bool focgold_healing_uses_highest_die(focgold_healing_method method);

bool focgold_animal_head_shot_releases_gas(void);
int focgold_animal_head_shot_success_threshold(void);
bool focgold_resolve_animal_head_shot(bool attack_hit_head,
                                      bool *head_shot_success);
int focgold_animal_gas_attack_required_rolls(void);
bool focgold_animal_gas_attack_halves_movement(void);
int focgold_animal_gas_attack_movement_inches(focgold_movement_pace pace,
                                              const focgold_skills *skills,
                                              const focgold_wounds *wounds);
int focgold_animal_gas_initial_radius_inches(void);
int focgold_animal_gas_shrink_per_turn_inches(void);
int focgold_animal_gas_drift_inches_per_turn(void);
int focgold_animal_gas_drift_direction(void);
int focgold_foe_attack_modifier_dice(focgold_foe_type foe);
int focgold_foe_movement_modifier_inches(focgold_foe_type foe);
int focgold_foe_movement_inches(focgold_foe_type foe,
                                focgold_movement_pace pace,
                                const focgold_skills *skills,
                                const focgold_wounds *wounds);
int focgold_soldier_armor_save_threshold(void);
bool focgold_damage_counts_as_shot_for_armor(focgold_damage_source source,
                                             bool referee_counts_grenade);
bool focgold_resolve_soldier_armor_save(focgold_damage_source source,
                                        bool referee_counts_grenade,
                                        bool *saved);
bool focgold_apply_damage_with_soldier_armor(focgold_wounds *wounds,
                                             focgold_damage_source source,
                                             bool referee_counts_grenade,
                                             focgold_hit_location location,
                                             int wounds_inflicted,
                                             bool *saved);

bool focgold_resolve_ranged_attack(const focgold_character *attacker,
                                   const focgold_character *target,
                                   focgold_range_band range,
                                   const focgold_attack_modifiers *modifiers,
                                   bool called_head_shot,
                                   focgold_attack_result *result);
bool focgold_resolve_melee(const focgold_character *attacker,
                           focgold_melee_attack attack,
                           focgold_melee_result *result);
bool focgold_resolve_healing(const focgold_character *healer,
                             const focgold_character *target,
                             focgold_healing_method method,
                             focgold_healing_result *result);

#ifdef __cplusplus
}
#endif

#endif
