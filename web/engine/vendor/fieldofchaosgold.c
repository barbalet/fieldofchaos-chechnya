#include "fieldofchaosgold.h"
#include "fieldofchaosgold_internal.h"

#include <string.h>

static unsigned int focgold_rng_state = 1u;

static unsigned int focgold_next_random(void) {
    focgold_rng_state = focgold_rng_state * 1664525u + 1013904223u;
    return focgold_rng_state;
}

void focgold_seed(unsigned int seed) {
    focgold_rng_state = seed;
}

int focgold_roll_d6(void) {
    return (int)(((focgold_next_random() >> 16) % 6u) + 1u);
}

static int focgold_roll_die_sides(int sides) {
    if (sides <= 0 || sides > 6 || (6 % sides) != 0) {
        return 0;
    }

    return ((focgold_roll_d6() - 1) % sides) + 1;
}

int focgold_roll_d6_sum(int dice_count) {
    int total = 0;
    int index;

    if (dice_count <= 0) {
        return 0;
    }

    for (index = 0; index < dice_count; index++) {
        total += focgold_roll_d6();
    }

    return total;
}

int focgold_roll_d6_highest(int dice_count) {
    int highest = 0;
    int index;

    if (dice_count <= 0) {
        return 0;
    }

    for (index = 0; index < dice_count; index++) {
        int roll = focgold_roll_d6();
        if (roll > highest) {
            highest = roll;
        }
    }

    return highest;
}

int focgold_roll_damage(focgold_damage_roll roll) {
    int total = 0;
    int index;

    if (roll.dice_count <= 0 || roll.die_sides <= 0) {
        return 0;
    }

    for (index = 0; index < roll.dice_count; index++) {
        total += focgold_roll_die_sides(roll.die_sides);
    }

    return total;
}

int focgold_stat_total(const focgold_stats *stats) {
    if (stats == 0) {
        return 0;
    }

    return stats->regular_intelligence +
           stats->irregular_intelligence +
           stats->appearance +
           stats->physical_health +
           stats->mental_health;
}

int focgold_stat_value(const focgold_stats *stats, focgold_stat_id stat) {
    if (stats == 0) {
        return 0;
    }

    switch (stat) {
    case focgold_stat_regular_intelligence:
        return stats->regular_intelligence;
    case focgold_stat_irregular_intelligence:
        return stats->irregular_intelligence;
    case focgold_stat_appearance:
        return stats->appearance;
    case focgold_stat_physical_health:
        return stats->physical_health;
    case focgold_stat_mental_health:
        return stats->mental_health;
    case focgold_stat_count:
        break;
    }

    return 0;
}

static bool focgold_stats_have_valid_values(const focgold_stats *stats) {
    if (stats == 0) {
        return false;
    }

    return stats->regular_intelligence >= 0 && stats->regular_intelligence <= 10 &&
           stats->irregular_intelligence >= 0 && stats->irregular_intelligence <= 10 &&
           stats->appearance >= 0 && stats->appearance <= 10 &&
           stats->physical_health >= 0 && stats->physical_health <= 10 &&
           stats->mental_health >= 0 && stats->mental_health <= 10;
}

bool focgold_validate_initial_stats(const focgold_stats *stats) {
    return focgold_stats_have_valid_values(stats) &&
           focgold_stat_total(stats) <= 30;
}

bool focgold_validate_long_term_stats(const focgold_stats *stats) {
    return focgold_stats_have_valid_values(stats) &&
           focgold_stat_total(stats) <= 40;
}

static bool focgold_is_permutation_of_five(const size_t values[5]) {
    bool seen[5] = {false, false, false, false, false};
    size_t index;

    for (index = 0; index < 5; index++) {
        if (values[index] >= 5 || seen[values[index]]) {
            return false;
        }
        seen[values[index]] = true;
    }

    return true;
}

static bool focgold_dice_are_valid(const int dice[3]) {
    size_t index;

    for (index = 0; index < 3; index++) {
        if (dice[index] < 1 || dice[index] > 6) {
            return false;
        }
    }

    return true;
}

bool focgold_generate_stats(const focgold_stat_generation_choice *choice,
                            focgold_stats *stats) {
    int values[5];
    size_t index;

    if (choice == 0 || stats == 0) {
        return false;
    }

    if (!focgold_dice_are_valid(choice->rolled_dice) ||
        choice->first_inverted_die >= 3 ||
        choice->second_inverted_die >= 3 ||
        choice->first_inverted_die == choice->second_inverted_die ||
        choice->plus_two_value >= 5 ||
        !focgold_is_permutation_of_five(choice->stat_value_indices)) {
        return false;
    }

    values[0] = choice->rolled_dice[0];
    values[1] = choice->rolled_dice[1];
    values[2] = choice->rolled_dice[2];
    values[3] = 7 - choice->rolled_dice[choice->first_inverted_die];
    values[4] = 7 - choice->rolled_dice[choice->second_inverted_die];

    for (index = 0; index < 5; index++) {
        values[index] += index == choice->plus_two_value ? 2 : 1;
    }

    stats->regular_intelligence = values[choice->stat_value_indices[focgold_stat_regular_intelligence]];
    stats->irregular_intelligence = values[choice->stat_value_indices[focgold_stat_irregular_intelligence]];
    stats->appearance = values[choice->stat_value_indices[focgold_stat_appearance]];
    stats->physical_health = values[choice->stat_value_indices[focgold_stat_physical_health]];
    stats->mental_health = values[choice->stat_value_indices[focgold_stat_mental_health]];

    return focgold_validate_initial_stats(stats);
}

const char *focgold_stat_name(focgold_stat_id stat) {
    static const char *const names[focgold_stat_count] = {
        "Regular Intelligence",
        "Irregular Intelligence",
        "Appearance",
        "Physical Health",
        "Mental Health"
    };

    if (stat < 0 || stat >= focgold_stat_count) {
        return 0;
    }

    return names[stat];
}

int focgold_skill_value(const focgold_skills *skills, focgold_skill_id skill) {
    if (skills == 0) {
        return 0;
    }

    switch (skill) {
    case focgold_skill_firearm_basic:
        return skills->firearm_basic;
    case focgold_skill_firearm_advanced:
        return skills->firearm_advanced;
    case focgold_skill_close_combat:
        return skills->close_combat;
    case focgold_skill_improvised_weapon_basic:
        return skills->improvised_weapon_basic;
    case focgold_skill_clandestine_weapon_basic:
        return skills->clandestine_weapon_basic;
    case focgold_skill_carpentry:
        return skills->carpentry;
    case focgold_skill_manufacture_clandestine_weapon:
        return skills->manufacture_clandestine_weapon;
    case focgold_skill_chemistry_basic:
        return skills->chemistry_basic;
    case focgold_skill_explosive_engineering:
        return skills->explosive_engineering;
    case focgold_skill_biology_basic:
        return skills->biology_basic;
    case focgold_skill_chemistry_advanced:
        return skills->chemistry_advanced;
    case focgold_skill_chemistry_pharmaceutical:
        return skills->chemistry_pharmaceutical;
    case focgold_skill_first_aid:
        return skills->first_aid;
    case focgold_skill_paramedic:
        return skills->paramedic;
    case focgold_skill_evade:
        return skills->evade;
    case focgold_skill_marching:
        return skills->marching;
    case focgold_skill_running:
        return skills->running;
    case focgold_skill_count:
        break;
    }

    return 0;
}

bool focgold_validate_skills(const focgold_skills *skills) {
    int skill;

    if (skills == 0) {
        return false;
    }

    for (skill = 0; skill < focgold_skill_count; skill++) {
        int value = focgold_skill_value(skills, (focgold_skill_id)skill);
        if (value < 0 || value > 100) {
            return false;
        }
    }

    return true;
}

const char *focgold_skill_name(focgold_skill_id skill) {
    static const char *const names[focgold_skill_count] = {
        "Firearm Use, Basic",
        "Firearm Use, Advanced",
        "Close Combat",
        "Improvised Weapon Use, Basic",
        "Clandestine Weapon Use, Basic",
        "Carpentry",
        "Manufacture Clandestine Weapon",
        "Chemistry, Basic",
        "Explosive Engineering",
        "Biology, Basic",
        "Chemistry, Advanced",
        "Chemistry, Pharmaceutical",
        "First Aid",
        "Paramedic",
        "Evade",
        "Marching",
        "Running"
    };

    if (skill < 0 || skill >= focgold_skill_count) {
        return 0;
    }

    return names[skill];
}

focgold_stat_id focgold_skill_stat(focgold_skill_id skill) {
    static const focgold_stat_id stats[focgold_skill_count] = {
        focgold_stat_physical_health,
        focgold_stat_mental_health,
        focgold_stat_physical_health,
        focgold_stat_irregular_intelligence,
        focgold_stat_irregular_intelligence,
        focgold_stat_physical_health,
        focgold_stat_irregular_intelligence,
        focgold_stat_regular_intelligence,
        focgold_stat_irregular_intelligence,
        focgold_stat_regular_intelligence,
        focgold_stat_regular_intelligence,
        focgold_stat_regular_intelligence,
        focgold_stat_regular_intelligence,
        focgold_stat_regular_intelligence,
        focgold_stat_physical_health,
        focgold_stat_physical_health,
        focgold_stat_physical_health
    };

    if (skill < 0 || skill >= focgold_skill_count) {
        return focgold_stat_count;
    }

    return stats[skill];
}

const focgold_skill_id *focgold_skill_prerequisites(focgold_skill_id skill,
                                                    size_t *count) {
    static const focgold_skill_id firearm_advanced[] = {
        focgold_skill_firearm_basic
    };
    static const focgold_skill_id manufacture_clandestine_weapon[] = {
        focgold_skill_carpentry
    };
    static const focgold_skill_id explosive_engineering[] = {
        focgold_skill_chemistry_basic
    };
    static const focgold_skill_id chemistry_advanced[] = {
        focgold_skill_biology_basic,
        focgold_skill_chemistry_basic
    };
    static const focgold_skill_id chemistry_pharmaceutical[] = {
        focgold_skill_chemistry_advanced
    };
    static const focgold_skill_id paramedic[] = {
        focgold_skill_first_aid
    };

    if (count != 0) {
        *count = 0;
    }

    switch (skill) {
    case focgold_skill_firearm_advanced:
        if (count != 0) {
            *count = 1;
        }
        return firearm_advanced;
    case focgold_skill_manufacture_clandestine_weapon:
        if (count != 0) {
            *count = 1;
        }
        return manufacture_clandestine_weapon;
    case focgold_skill_explosive_engineering:
        if (count != 0) {
            *count = 1;
        }
        return explosive_engineering;
    case focgold_skill_chemistry_advanced:
        if (count != 0) {
            *count = 2;
        }
        return chemistry_advanced;
    case focgold_skill_chemistry_pharmaceutical:
        if (count != 0) {
            *count = 1;
        }
        return chemistry_pharmaceutical;
    case focgold_skill_paramedic:
        if (count != 0) {
            *count = 1;
        }
        return paramedic;
    case focgold_skill_firearm_basic:
    case focgold_skill_close_combat:
    case focgold_skill_improvised_weapon_basic:
    case focgold_skill_clandestine_weapon_basic:
    case focgold_skill_carpentry:
    case focgold_skill_chemistry_basic:
    case focgold_skill_biology_basic:
    case focgold_skill_first_aid:
    case focgold_skill_evade:
    case focgold_skill_marching:
    case focgold_skill_running:
    case focgold_skill_count:
        break;
    }

    return 0;
}

bool focgold_skill_improves_healing(focgold_skill_id skill) {
    return skill == focgold_skill_first_aid ||
           skill == focgold_skill_paramedic;
}

static bool focgold_skill_is_selected(const focgold_skills *skills,
                                      focgold_skill_id skill) {
    return focgold_skill_value(skills, skill) > 0;
}

size_t focgold_skill_count_for_stat(const focgold_skills *skills,
                                    focgold_stat_id stat) {
    size_t count = 0;
    int skill;

    if (skills == 0 || stat < 0 || stat >= focgold_stat_count) {
        return 0;
    }

    for (skill = 0; skill < focgold_skill_count; skill++) {
        focgold_skill_id skill_id = (focgold_skill_id)skill;
        if (focgold_skill_stat(skill_id) == stat &&
            focgold_skill_is_selected(skills, skill_id)) {
            count++;
        }
    }

    return count;
}

bool focgold_validate_skill_prerequisites(const focgold_skills *skills) {
    int skill;

    if (skills == 0) {
        return false;
    }

    for (skill = 0; skill < focgold_skill_count; skill++) {
        focgold_skill_id skill_id = (focgold_skill_id)skill;
        const focgold_skill_id *prerequisites;
        size_t prerequisite_count = 0;
        size_t prerequisite_index;

        if (!focgold_skill_is_selected(skills, skill_id)) {
            continue;
        }

        prerequisites = focgold_skill_prerequisites(skill_id,
                                                    &prerequisite_count);
        for (prerequisite_index = 0;
             prerequisite_index < prerequisite_count;
             prerequisite_index++) {
            if (!focgold_skill_is_selected(skills,
                                           prerequisites[prerequisite_index])) {
                return false;
            }
        }
    }

    return true;
}

bool focgold_validate_character_skills(const focgold_character *character) {
    int stat;

    if (character == 0 ||
        !focgold_stats_have_valid_values(&character->stats) ||
        !focgold_validate_skills(&character->skills) ||
        !focgold_validate_skill_prerequisites(&character->skills)) {
        return false;
    }

    for (stat = 0; stat < focgold_stat_count; stat++) {
        focgold_stat_id stat_id = (focgold_stat_id)stat;
        if ((int)focgold_skill_count_for_stat(&character->skills, stat_id) >
            focgold_stat_value(&character->stats, stat_id)) {
            return false;
        }
    }

    return true;
}

const char *focgold_weapon_name(focgold_weapon weapon) {
    static const char *const names[focgold_weapon_count] = {
        "Sniper Rifle",
        "Rifle",
        "Carbine",
        "Automatic",
        "SubMG",
        "Shotgun"
    };

    if (weapon < 0 || weapon >= focgold_weapon_count) {
        return 0;
    }

    return names[weapon];
}

bool focgold_parse_weapon(const char *name, focgold_weapon *weapon) {
    int index;

    if (name == 0 || weapon == 0) {
        return false;
    }

    for (index = 0; index < focgold_weapon_count; index++) {
        const focgold_weapon current = (focgold_weapon)index;
        if (strcmp(name, focgold_weapon_name(current)) == 0) {
            *weapon = current;
            return true;
        }
    }

    return false;
}

bool focgold_weapon_uses_firearm_basic(focgold_weapon weapon) {
    return weapon >= 0 && weapon < focgold_weapon_count;
}

int focgold_weapon_range_inches(focgold_weapon weapon,
                                focgold_range_band range) {
    static const int ranges[focgold_weapon_count][3] = {
        {24, 36, 48},
        {18, 27, 36},
        {12, 18, 24},
        {8, 12, 16},
        {6, 9, 12},
        {0, 0, 0}
    };

    if (weapon < 0 || weapon >= focgold_weapon_count ||
        range < 0 || range > focgold_range_long) {
        return 0;
    }

    return ranges[weapon][range];
}

int focgold_shotgun_total_length_inches(void) {
    return 15;
}

int focgold_shotgun_band_max_inches(focgold_shotgun_band band) {
    static const int maximums[focgold_shotgun_band_count] = {
        5,
        10,
        15
    };

    if (band < 0 || band >= focgold_shotgun_band_count) {
        return 0;
    }

    return maximums[band];
}

int focgold_shotgun_band_width_inches(focgold_shotgun_band band) {
    static const int widths[focgold_shotgun_band_count] = {
        1,
        2,
        3
    };

    if (band < 0 || band >= focgold_shotgun_band_count) {
        return 0;
    }

    return widths[band];
}

focgold_damage_roll focgold_shotgun_band_wounds(focgold_shotgun_band band) {
    static const focgold_damage_roll rolls[focgold_shotgun_band_count] = {
        {2, 6},
        {1, 6},
        {1, 3}
    };
    const focgold_damage_roll none = {0, 0};

    if (band < 0 || band >= focgold_shotgun_band_count) {
        return none;
    }

    return rolls[band];
}

static int focgold_absolute_int(int value) {
    return value < 0 ? -value : value;
}

static void focgold_initialize_area_results(const focgold_area_target *targets,
                                            size_t target_count,
                                            focgold_area_damage *results) {
    size_t index;

    for (index = 0; index < target_count; index++) {
        size_t location_index;

        memset(&results[index], 0, sizeof(results[index]));
        results[index].id = targets[index].id;
        results[index].ally = targets[index].ally;
        results[index].shotgun_band = focgold_shotgun_band_count;
        results[index].grenade_band = focgold_grenade_band_count;

        for (location_index = 0;
             location_index < focgold_area_max_wounds;
             location_index++) {
            results[index].hit_locations[location_index] = focgold_hit_chest;
        }
    }
}

static void focgold_apply_area_damage(focgold_damage_roll roll,
                                      focgold_area_damage *result) {
    int wound_index;
    int wounds = focgold_roll_damage(roll);

    if (wounds > focgold_area_max_wounds) {
        wounds = focgold_area_max_wounds;
    }

    result->affected = true;
    result->wounds_inflicted = wounds;
    for (wound_index = 0; wound_index < wounds; wound_index++) {
        result->hit_locations[wound_index] = focgold_roll_blast_hit_location();
    }
}

bool focgold_shotgun_band_for_target(int distance_inches,
                                     int lateral_inches,
                                     focgold_shotgun_band *band) {
    focgold_shotgun_band candidate;
    int lateral_distance;

    if (band == 0 || distance_inches < 0) {
        return false;
    }

    lateral_distance = focgold_absolute_int(lateral_inches);
    for (candidate = focgold_shotgun_near;
         candidate < focgold_shotgun_band_count;
         candidate++) {
        int minimum = candidate == focgold_shotgun_near ?
                      0 :
                      focgold_shotgun_band_max_inches(
                          (focgold_shotgun_band)(candidate - 1)) + 1;
        int maximum = focgold_shotgun_band_max_inches(candidate);
        int width = focgold_shotgun_band_width_inches(candidate);

        if (distance_inches >= minimum && distance_inches <= maximum &&
            lateral_distance <= width) {
            *band = candidate;
            return true;
        }
    }

    return false;
}

bool focgold_resolve_shotgun_area(const focgold_area_target *targets,
                                  size_t target_count,
                                  focgold_area_damage *results,
                                  size_t result_count,
                                  size_t *affected_count) {
    size_t index;
    size_t affected = 0;
    focgold_shotgun_band nearest_band = focgold_shotgun_band_count;

    if (target_count == 0) {
        if (affected_count != 0) {
            *affected_count = 0;
        }
        return true;
    }
    if (targets == 0 || results == 0 || result_count < target_count) {
        return false;
    }

    focgold_initialize_area_results(targets, target_count, results);

    for (index = 0; index < target_count; index++) {
        focgold_shotgun_band band;
        if (focgold_shotgun_band_for_target(targets[index].distance_inches,
                                            targets[index].lateral_inches,
                                            &band) &&
            band < nearest_band) {
            nearest_band = band;
        }
    }

    if (nearest_band == focgold_shotgun_band_count) {
        if (affected_count != 0) {
            *affected_count = 0;
        }
        return true;
    }

    for (index = 0; index < target_count; index++) {
        focgold_shotgun_band band;
        if (focgold_shotgun_band_for_target(targets[index].distance_inches,
                                            targets[index].lateral_inches,
                                            &band) &&
            band == nearest_band) {
            results[index].shotgun_band = band;
            focgold_apply_area_damage(focgold_shotgun_band_wounds(band),
                                      &results[index]);
            affected++;
        }
    }

    if (affected_count != 0) {
        *affected_count = affected;
    }

    return true;
}

int focgold_grenade_throw_range_inches(void) {
    return 12;
}

int focgold_grenade_radius_inches(focgold_grenade_band band,
                                  bool inside_building) {
    static const int open_radii[focgold_grenade_band_count] = {
        1,
        3,
        4
    };
    static const int building_radii[focgold_grenade_band_count] = {
        3,
        6,
        9
    };

    if (band < 0 || band >= focgold_grenade_band_count) {
        return 0;
    }

    return inside_building ? building_radii[band] : open_radii[band];
}

focgold_damage_roll focgold_grenade_band_wounds(focgold_grenade_band band) {
    static const focgold_damage_roll rolls[focgold_grenade_band_count] = {
        {1, 6},
        {1, 3},
        {1, 2}
    };
    const focgold_damage_roll none = {0, 0};

    if (band < 0 || band >= focgold_grenade_band_count) {
        return none;
    }

    return rolls[band];
}

bool focgold_grenade_band_for_distance(int distance_inches,
                                       bool inside_building,
                                       focgold_grenade_band *band) {
    focgold_grenade_band candidate;

    if (band == 0 || distance_inches < 0) {
        return false;
    }

    for (candidate = focgold_grenade_inner;
         candidate < focgold_grenade_band_count;
         candidate++) {
        int minimum = candidate == focgold_grenade_inner ?
                      0 :
                      focgold_grenade_radius_inches(
                          (focgold_grenade_band)(candidate - 1),
                          inside_building) + 1;
        int maximum = focgold_grenade_radius_inches(candidate,
                                                    inside_building);

        if (distance_inches >= minimum && distance_inches <= maximum) {
            *band = candidate;
            return true;
        }
    }

    return false;
}

bool focgold_resolve_grenade_area(const focgold_area_target *targets,
                                  size_t target_count,
                                  bool inside_building,
                                  bool dud,
                                  focgold_area_damage *results,
                                  size_t result_count,
                                  size_t *affected_count) {
    size_t index;
    size_t affected = 0;

    if (target_count == 0) {
        if (affected_count != 0) {
            *affected_count = 0;
        }
        return true;
    }
    if (targets == 0 || results == 0 || result_count < target_count) {
        return false;
    }

    focgold_initialize_area_results(targets, target_count, results);

    if (dud) {
        if (affected_count != 0) {
            *affected_count = 0;
        }
        return true;
    }

    for (index = 0; index < target_count; index++) {
        focgold_grenade_band band;
        if (focgold_grenade_band_for_distance(targets[index].distance_inches,
                                              inside_building,
                                              &band)) {
            results[index].grenade_band = band;
            focgold_apply_area_damage(focgold_grenade_band_wounds(band),
                                      &results[index]);
            affected++;
        }
    }

    if (affected_count != 0) {
        *affected_count = affected;
    }

    return true;
}

bool focgold_grenade_uses_skill(void) {
    return false;
}

bool focgold_grenade_skill_modifies_reliability(focgold_skill_id skill) {
    (void)skill;
    return false;
}

bool focgold_resolve_grenade_reliability(focgold_grenade_reliability_result *result) {
    int total;

    if (result == 0) {
        return false;
    }

    total = focgold_roll_d6_sum(focgold_grenade_reliability_dice);
    result->dice_total = total;
    result->dud = total <= focgold_grenade_dud_threshold;

    return true;
}

const char *focgold_range_name(focgold_range_band range) {
    static const char *const names[] = {
        "Close",
        "Standard",
        "Long"
    };

    if (range < 0 || range > focgold_range_long) {
        return 0;
    }

    return names[range];
}

int focgold_ranged_base_dice(focgold_range_band range) {
    static const int dice[] = {
        1,
        2,
        3
    };

    if (range < 0 || range > focgold_range_long) {
        return 0;
    }

    return dice[range];
}

int focgold_ranged_skill_dice(const focgold_skills *skills) {
    if (skills == 0) {
        return 0;
    }

    if (focgold_skill_is_selected(skills, focgold_skill_firearm_advanced)) {
        return 2;
    }
    if (focgold_skill_is_selected(skills, focgold_skill_firearm_basic)) {
        return 1;
    }

    return 0;
}

int focgold_ranged_hit_threshold(focgold_range_band range) {
    static const int thresholds[] = {
        4,
        10,
        16
    };

    if (range < 0 || range > focgold_range_long) {
        return 0;
    }

    return thresholds[range];
}

int focgold_ranged_head_shot_threshold(focgold_range_band range) {
    static const int thresholds[] = {
        6,
        12,
        18
    };

    if (range < 0 || range > focgold_range_long) {
        return 0;
    }

    return thresholds[range];
}

int focgold_ranged_modifier_dice(const focgold_attack_modifiers *modifiers) {
    focgold_cover cover;
    int modifier = 0;

    if (modifiers == 0) {
        return 0;
    }

    cover = modifiers->cover;
    if (modifiers->line_crosses_grenade_debris &&
        cover == focgold_cover_none) {
        cover = focgold_cover_light;
    }

    switch (cover) {
    case focgold_cover_light:
        modifier -= 1;
        break;
    case focgold_cover_heavy:
        modifier -= 2;
        break;
    case focgold_cover_none:
        break;
    }

    switch (modifiers->target_movement) {
    case focgold_target_movement_standard:
        modifier -= 1;
        break;
    case focgold_target_movement_fast:
        modifier -= 2;
        break;
    case focgold_target_movement_none:
        break;
    }

    if (modifiers->target_has_evade) {
        modifier -= 1;
    }

    return modifier;
}

int focgold_weapon_shots_per_turn(focgold_weapon weapon,
                                  bool has_firearm_advanced) {
    switch (weapon) {
    case focgold_weapon_rifle:
    case focgold_weapon_carbine:
        return has_firearm_advanced ? 2 : 1;
    case focgold_weapon_automatic:
        return 2;
    case focgold_weapon_submg:
        return 3;
    case focgold_weapon_sniper_rifle:
    case focgold_weapon_shotgun:
        return 1;
    case focgold_weapon_count:
        break;
    }

    return 0;
}

focgold_movement_pace focgold_weapon_movement_rule(focgold_weapon weapon) {
    switch (weapon) {
    case focgold_weapon_sniper_rifle:
        return focgold_movement_very_slow;
    case focgold_weapon_rifle:
        return focgold_movement_slow;
    case focgold_weapon_carbine:
    case focgold_weapon_automatic:
    case focgold_weapon_shotgun:
        return focgold_movement_standard;
    case focgold_weapon_submg:
        return focgold_movement_fast;
    case focgold_weapon_count:
        break;
    }

    return focgold_movement_standard;
}

bool focgold_weapon_has_referee_movement_rule(focgold_weapon weapon) {
    return weapon == focgold_weapon_shotgun;
}

int focgold_weapon_minimum_range_inches(focgold_weapon weapon) {
    return weapon == focgold_weapon_sniper_rifle ? 12 : 0;
}

bool focgold_weapon_can_fire_at_distance(focgold_weapon weapon,
                                         int distance_inches) {
    int minimum_range;

    if (weapon < 0 || weapon >= focgold_weapon_count || distance_inches < 0) {
        return false;
    }

    minimum_range = focgold_weapon_minimum_range_inches(weapon);
    return distance_inches >= minimum_range;
}

bool focgold_weapon_can_head_shot(focgold_weapon weapon) {
    return weapon == focgold_weapon_sniper_rifle ||
           weapon == focgold_weapon_rifle ||
           weapon == focgold_weapon_carbine;
}

int focgold_weapon_jam_dice_count(focgold_weapon weapon) {
    switch (weapon) {
    case focgold_weapon_automatic:
        return 2;
    case focgold_weapon_submg:
        return 1;
    case focgold_weapon_sniper_rifle:
    case focgold_weapon_rifle:
    case focgold_weapon_carbine:
    case focgold_weapon_shotgun:
    case focgold_weapon_count:
        break;
    }

    return 0;
}

int focgold_weapon_jam_threshold(focgold_weapon weapon) {
    switch (weapon) {
    case focgold_weapon_automatic:
    case focgold_weapon_submg:
        return 1;
    case focgold_weapon_sniper_rifle:
    case focgold_weapon_rifle:
    case focgold_weapon_carbine:
    case focgold_weapon_shotgun:
    case focgold_weapon_count:
        break;
    }

    return 0;
}

bool focgold_resolve_weapon_jam(focgold_weapon weapon, bool *jammed) {
    int dice_count;
    int threshold;

    if (jammed == 0) {
        return false;
    }

    dice_count = focgold_weapon_jam_dice_count(weapon);
    threshold = focgold_weapon_jam_threshold(weapon);
    if (dice_count == 0 || threshold == 0) {
        *jammed = false;
        return true;
    }

    *jammed = focgold_roll_d6_sum(dice_count) <= threshold;
    return true;
}

int focgold_reload_turn_count(void) {
    return focgold_reload_turns;
}

int focgold_clear_jam_turn_count(void) {
    return focgold_clear_jam_turns;
}

bool focgold_apply_ranged_attack_ammo(focgold_character *attacker,
                                      const focgold_attack_result *result) {
    if (attacker == 0 || result == 0 || result->rounds_spent < 0) {
        return false;
    }

    if (result->rounds_spent > attacker->rounds_in_clip) {
        attacker->rounds_in_clip = 0;
        return false;
    }

    attacker->rounds_in_clip -= result->rounds_spent;
    return true;
}

bool focgold_reload_character(focgold_character *character) {
    if (character == 0 || character->clips <= 0) {
        return false;
    }

    character->clips--;
    character->rounds_in_clip = focgold_standard_clip_rounds;
    return true;
}

bool focgold_clear_jam_state(bool *jammed) {
    if (jammed == 0) {
        return false;
    }

    *jammed = false;
    return true;
}

int focgold_called_head_shot_required_setup_moves(void) {
    return focgold_called_head_shot_setup_moves;
}

bool focgold_called_head_shot_ready(int moves_declared_before_firing) {
    return moves_declared_before_firing >= focgold_called_head_shot_setup_moves;
}

bool focgold_called_head_shot_miss_is_total_miss(void) {
    return true;
}

int focgold_called_head_shot_progress_after_turn(int moves_declared_before_firing,
                                                 bool spent_setup_move) {
    int progress;

    if (moves_declared_before_firing < 0) {
        return 0;
    }
    if (!spent_setup_move) {
        return 0;
    }

    progress = moves_declared_before_firing + 1;
    if (progress > focgold_called_head_shot_setup_moves) {
        progress = focgold_called_head_shot_setup_moves;
    }

    return progress;
}

static int focgold_skill_enabled(int skill_value) {
    return skill_value > 0;
}

static int focgold_disabled_leg_count(const focgold_wounds *wounds) {
    int disabled = 0;

    if (wounds == 0) {
        return 0;
    }

    if (wounds->left_leg <= 0) {
        disabled++;
    }
    if (wounds->right_leg <= 0) {
        disabled++;
    }

    return disabled;
}

int focgold_movement_inches(focgold_movement_pace pace,
                            const focgold_skills *skills,
                            const focgold_wounds *wounds) {
    int movement;
    int disabled_legs;

    switch (pace) {
    case focgold_movement_very_slow:
        movement = 2;
        if (skills != 0 && focgold_skill_enabled(skills->evade)) {
            movement += 1;
        }
        break;
    case focgold_movement_slow:
        movement = 3;
        if (skills != 0 && focgold_skill_enabled(skills->marching)) {
            movement += 1;
        }
        break;
    case focgold_movement_standard:
        movement = 5;
        if (skills != 0 && focgold_skill_enabled(skills->marching)) {
            movement += 1;
        }
        break;
    case focgold_movement_fast:
        movement = 8;
        if (skills != 0 && focgold_skill_enabled(skills->running)) {
            movement += 2;
        }
        break;
    default:
        return 0;
    }

    disabled_legs = focgold_disabled_leg_count(wounds);
    if (disabled_legs >= 2) {
        return 0;
    }
    if (disabled_legs == 1) {
        movement /= 2;
    }

    return movement;
}

int focgold_movement_after_one_grenade_inches(focgold_movement_pace pace,
                                              const focgold_skills *skills,
                                              const focgold_wounds *wounds) {
    return focgold_movement_inches(pace, skills, wounds) / 2;
}

bool focgold_can_throw_two_grenades(bool stationary) {
    return stationary;
}

focgold_turn_permissions focgold_two_grenade_turn_permissions(void) {
    focgold_turn_permissions permissions = {
        false,
        false,
        false,
        false,
        false,
        false,
        false
    };

    return permissions;
}

void focgold_default_wounds(focgold_wounds *wounds) {
    if (wounds == 0) {
        return;
    }

    wounds->head = 1;
    wounds->chest = 4;
    wounds->abdomen = 2;
    wounds->left_arm = 1;
    wounds->right_arm = 1;
    wounds->left_leg = 2;
    wounds->right_leg = 2;
}

static int *focgold_wound_slot(focgold_wounds *wounds,
                               focgold_hit_location location) {
    if (wounds == 0) {
        return 0;
    }

    switch (location) {
    case focgold_hit_left_leg:
        return &wounds->left_leg;
    case focgold_hit_right_leg:
        return &wounds->right_leg;
    case focgold_hit_chest:
        return &wounds->chest;
    case focgold_hit_abdomen:
        return &wounds->abdomen;
    case focgold_hit_left_arm:
        return &wounds->left_arm;
    case focgold_hit_right_arm:
        return &wounds->right_arm;
    case focgold_hit_head:
        return &wounds->head;
    }

    return 0;
}

int focgold_wound_value(const focgold_wounds *wounds,
                        focgold_hit_location location) {
    focgold_wounds *mutable_wounds = (focgold_wounds *)wounds;
    int *slot = focgold_wound_slot(mutable_wounds, location);

    return slot == 0 ? 0 : *slot;
}

bool focgold_apply_wounds(focgold_wounds *wounds,
                          focgold_hit_location location,
                          int wounds_inflicted) {
    int *slot = focgold_wound_slot(wounds, location);

    if (slot == 0 || wounds_inflicted < 0) {
        return false;
    }

    if (wounds_inflicted >= *slot) {
        *slot = 0;
    } else {
        *slot -= wounds_inflicted;
    }

    return true;
}

bool focgold_apply_area_damage_to_wounds(focgold_wounds *wounds,
                                         const focgold_area_damage *damage) {
    int index;

    if (wounds == 0 || damage == 0 || damage->wounds_inflicted < 0) {
        return false;
    }
    if (!damage->affected) {
        return true;
    }

    for (index = 0;
         index < damage->wounds_inflicted && index < focgold_area_max_wounds;
         index++) {
        if (!focgold_apply_wounds(wounds, damage->hit_locations[index], 1)) {
            return false;
        }
    }

    return true;
}

bool focgold_recover_wound(focgold_wounds *current,
                           const focgold_wounds *maximum,
                           focgold_hit_location location) {
    int *current_slot = focgold_wound_slot(current, location);
    int maximum_value = focgold_wound_value(maximum, location);

    if (current_slot == 0 || maximum == 0 || maximum_value < 0) {
        return false;
    }
    if (*current_slot >= maximum_value) {
        return false;
    }

    (*current_slot)++;
    return true;
}

bool focgold_apply_healing_result_to_location(focgold_character *target,
                                              const focgold_healing_result *result,
                                              focgold_hit_location location) {
    if (target == 0 || result == 0) {
        return false;
    }
    if (!result->recovered || result->wounds_recovered <= 0) {
        return true;
    }

    return focgold_recover_wound(&target->current_wounds,
                                 &target->maximum_wounds,
                                 location);
}

bool focgold_apply_healing_result(focgold_character *target,
                                  const focgold_healing_result *result) {
    if (result == 0) {
        return false;
    }

    return focgold_apply_healing_result_to_location(target,
                                                    result,
                                                    result->location);
}

int focgold_total_wounds(const focgold_wounds *wounds) {
    if (wounds == 0) {
        return 0;
    }

    return wounds->head +
           wounds->chest +
           wounds->abdomen +
           wounds->left_arm +
           wounds->right_arm +
           wounds->left_leg +
           wounds->right_leg;
}

bool focgold_is_unconscious(const focgold_wounds *wounds) {
    if (wounds == 0) {
        return false;
    }

    return wounds->head <= 0 ||
           wounds->chest <= 0 ||
           wounds->abdomen <= 0;
}

bool focgold_is_grave_condition(const focgold_wounds *wounds) {
    return focgold_total_wounds(wounds) > 0 &&
           focgold_total_wounds(wounds) < 6;
}

bool focgold_is_dead(const focgold_wounds *wounds) {
    return focgold_total_wounds(wounds) <= 0;
}

bool focgold_can_firearm(const focgold_wounds *wounds) {
    if (wounds == 0 || focgold_is_dead(wounds) ||
        focgold_is_unconscious(wounds)) {
        return false;
    }

    return wounds->left_arm > 0 && wounds->right_arm > 0;
}

focgold_hit_location focgold_hit_location_for_3d6_total(int total) {
    if (total >= 3 && total <= 8) {
        return (total % 2) == 0 ? focgold_hit_right_leg : focgold_hit_left_leg;
    }
    if (total >= 9 && total <= 13) {
        return focgold_hit_chest;
    }
    if (total >= 14 && total <= 15) {
        return focgold_hit_abdomen;
    }
    if (total >= 16 && total <= 17) {
        return (total % 2) == 0 ? focgold_hit_right_arm : focgold_hit_left_arm;
    }
    if (total == 18) {
        return focgold_hit_head;
    }

    return focgold_hit_chest;
}

focgold_hit_location focgold_roll_bullet_hit_location(void) {
    return focgold_hit_location_for_3d6_total(focgold_roll_d6_sum(3));
}

focgold_hit_location focgold_roll_blast_hit_location(void) {
    return focgold_roll_bullet_hit_location();
}

const char *focgold_hit_location_name(focgold_hit_location location) {
    static const char *const names[] = {
        "Left Leg",
        "Right Leg",
        "Chest",
        "Abdomen",
        "Left Arm",
        "Right Arm",
        "Head"
    };

    if (location < 0 || location > focgold_hit_head) {
        return 0;
    }

    return names[location];
}

int focgold_melee_base_dice(focgold_melee_attack attack) {
    switch (attack) {
    case focgold_melee_blow:
    case focgold_melee_weapon:
        return 1;
    }

    return 0;
}

int focgold_melee_hit_threshold(focgold_melee_attack attack) {
    switch (attack) {
    case focgold_melee_blow:
        return 3;
    case focgold_melee_weapon:
        return 4;
    }

    return 0;
}

bool focgold_melee_skill_applies(focgold_melee_attack attack,
                                 focgold_skill_id skill) {
    if (attack == focgold_melee_blow) {
        return skill == focgold_skill_close_combat;
    }
    if (attack == focgold_melee_weapon) {
        return skill == focgold_skill_improvised_weapon_basic ||
               skill == focgold_skill_clandestine_weapon_basic;
    }

    return false;
}

int focgold_melee_skill_dice(const focgold_skills *skills,
                             focgold_melee_attack attack) {
    int modifier = 0;

    if (skills == 0) {
        return 0;
    }

    if (focgold_melee_skill_applies(attack, focgold_skill_close_combat) &&
        focgold_skill_enabled(skills->close_combat)) {
        modifier++;
    }
    if (focgold_melee_skill_applies(attack, focgold_skill_improvised_weapon_basic) &&
        focgold_skill_enabled(skills->improvised_weapon_basic)) {
        modifier++;
    }
    if (focgold_melee_skill_applies(attack, focgold_skill_clandestine_weapon_basic) &&
        focgold_skill_enabled(skills->clandestine_weapon_basic)) {
        modifier++;
    }

    return modifier;
}

int focgold_melee_skill_modifier_dice(const focgold_skills *skills,
                                      focgold_melee_attack attack) {
    return focgold_melee_skill_dice(skills, attack);
}

bool focgold_resolve_melee(const focgold_character *attacker,
                           focgold_melee_attack attack,
                           focgold_melee_result *result) {
    int threshold;

    if (attacker == 0 || result == 0) {
        return false;
    }

    memset(result, 0, sizeof(*result));

    threshold = focgold_melee_hit_threshold(attack);
    if (threshold == 0) {
        return false;
    }

    result->skill_dice = focgold_melee_skill_dice(&attacker->skills, attack);
    result->dice_count = focgold_melee_base_dice(attack) + result->skill_dice;
    result->dice_total = focgold_roll_d6_sum(result->dice_count);
    result->required_to_hit = threshold;
    result->hit = result->dice_total >= threshold;
    result->location = result->hit ? focgold_roll_bullet_hit_location() :
                                     focgold_hit_chest;
    result->wounds_inflicted = result->hit ? 1 : 0;

    return true;
}

int focgold_healing_dice_count(focgold_healing_method method) {
    switch (method) {
    case focgold_healing_no_skill:
    case focgold_healing_bandage:
        return 1;
    case focgold_healing_first_aid:
        return 2;
    case focgold_healing_paramedic:
        return 3;
    }

    return 0;
}

int focgold_healing_required_to_recover(focgold_healing_method method) {
    switch (method) {
    case focgold_healing_no_skill:
        return 6;
    case focgold_healing_bandage:
    case focgold_healing_first_aid:
    case focgold_healing_paramedic:
        return 5;
    }

    return 0;
}

bool focgold_healing_uses_highest_die(focgold_healing_method method) {
    return method == focgold_healing_first_aid ||
           method == focgold_healing_paramedic;
}

bool focgold_animal_head_shot_releases_gas(void) {
    return true;
}

int focgold_animal_head_shot_success_threshold(void) {
    return 5;
}

bool focgold_resolve_animal_head_shot(bool attack_hit_head,
                                      bool *head_shot_success) {
    if (head_shot_success == 0) {
        return false;
    }

    if (!attack_hit_head) {
        *head_shot_success = false;
        return true;
    }

    *head_shot_success =
        focgold_roll_d6() >= focgold_animal_head_shot_success_threshold();
    return true;
}

int focgold_animal_gas_attack_required_rolls(void) {
    return 2;
}

bool focgold_animal_gas_attack_halves_movement(void) {
    return true;
}

int focgold_animal_gas_attack_movement_inches(focgold_movement_pace pace,
                                              const focgold_skills *skills,
                                              const focgold_wounds *wounds) {
    return focgold_movement_inches(pace, skills, wounds) / 2;
}

int focgold_animal_gas_initial_radius_inches(void) {
    return focgold_roll_d6() + 6;
}

int focgold_animal_gas_shrink_per_turn_inches(void) {
    return 2;
}

int focgold_animal_gas_drift_inches_per_turn(void) {
    return 2;
}

int focgold_animal_gas_drift_direction(void) {
    return focgold_roll_d6();
}

int focgold_foe_attack_modifier_dice(focgold_foe_type foe) {
    return foe == focgold_foe_animal ? 1 : 0;
}

int focgold_foe_movement_modifier_inches(focgold_foe_type foe) {
    return foe == focgold_foe_hunter ? 1 : 0;
}

int focgold_foe_movement_inches(focgold_foe_type foe,
                                focgold_movement_pace pace,
                                const focgold_skills *skills,
                                const focgold_wounds *wounds) {
    int movement = focgold_movement_inches(pace, skills, wounds);

    if (movement <= 0) {
        return movement;
    }

    return movement + focgold_foe_movement_modifier_inches(foe);
}

int focgold_soldier_armor_save_threshold(void) {
    return 5;
}

bool focgold_damage_counts_as_shot_for_armor(focgold_damage_source source,
                                             bool referee_counts_grenade) {
    switch (source) {
    case focgold_damage_bullet:
    case focgold_damage_shotgun:
        return true;
    case focgold_damage_grenade:
        return referee_counts_grenade;
    case focgold_damage_melee:
        return false;
    }

    return false;
}

bool focgold_resolve_soldier_armor_save(focgold_damage_source source,
                                        bool referee_counts_grenade,
                                        bool *saved) {
    if (saved == 0) {
        return false;
    }

    if (!focgold_damage_counts_as_shot_for_armor(source,
                                                referee_counts_grenade)) {
        *saved = false;
        return true;
    }

    *saved = focgold_roll_d6() >= focgold_soldier_armor_save_threshold();
    return true;
}

bool focgold_apply_damage_with_soldier_armor(focgold_wounds *wounds,
                                             focgold_damage_source source,
                                             bool referee_counts_grenade,
                                             focgold_hit_location location,
                                             int wounds_inflicted,
                                             bool *saved) {
    bool armor_saved = false;

    if (wounds == 0 || saved == 0 || wounds_inflicted < 0) {
        return false;
    }

    if (!focgold_resolve_soldier_armor_save(source,
                                            referee_counts_grenade,
                                            &armor_saved)) {
        return false;
    }

    *saved = armor_saved;
    if (armor_saved) {
        return true;
    }

    return focgold_apply_wounds(wounds, location, wounds_inflicted);
}

bool focgold_resolve_ranged_attack(const focgold_character *attacker,
                                   const focgold_character *target,
                                   focgold_range_band range,
                                   const focgold_attack_modifiers *modifiers,
                                   bool called_head_shot,
                                   focgold_attack_result *result) {
    int dice_count;
    int modifier_dice;
    bool has_firearm_advanced;

    (void)target;

    if (attacker == 0 || result == 0) {
        return false;
    }

    memset(result, 0, sizeof(*result));

    result->can_attack = focgold_can_firearm(&attacker->current_wounds);
    result->head_shot_allowed = focgold_weapon_can_head_shot(attacker->weapon);
    result->required_to_hit = focgold_ranged_hit_threshold(range);
    result->required_head_shot = focgold_ranged_head_shot_threshold(range);
    if (!result->can_attack || result->required_to_hit == 0) {
        return true;
    }

    result->skill_dice = focgold_ranged_skill_dice(&attacker->skills);
    modifier_dice = focgold_ranged_modifier_dice(modifiers);
    result->modifier_dice = modifier_dice;
    dice_count = focgold_ranged_base_dice(range) +
                 result->skill_dice +
                 modifier_dice;
    if (dice_count < 1) {
        dice_count = 1;
    }
    result->dice_count = dice_count;
    result->dice_total = focgold_roll_d6_sum(dice_count);

    has_firearm_advanced =
        focgold_skill_enabled(attacker->skills.firearm_advanced);
    result->shots_fired =
        focgold_weapon_shots_per_turn(attacker->weapon,
                                      has_firearm_advanced);
    result->rounds_spent = result->shots_fired;
    focgold_resolve_weapon_jam(attacker->weapon, &result->jammed);

    if (called_head_shot && result->head_shot_allowed) {
        result->head_shot = result->dice_total >= result->required_head_shot;
        result->hit = result->head_shot;
    } else {
        result->hit = result->dice_total >= result->required_to_hit;
    }

    result->location = result->head_shot ? focgold_hit_head :
                       result->hit ? focgold_roll_bullet_hit_location() :
                       focgold_hit_chest;
    result->wounds_inflicted = result->hit ? 1 : 0;

    return true;
}

bool focgold_resolve_healing(const focgold_character *healer,
                             const focgold_character *target,
                             focgold_healing_method method,
                             focgold_healing_result *result) {
    int dice_count;
    int required;

    (void)healer;
    (void)target;

    if (result == 0) {
        return false;
    }

    memset(result, 0, sizeof(*result));

    dice_count = focgold_healing_dice_count(method);
    required = focgold_healing_required_to_recover(method);
    if (dice_count == 0 || required == 0) {
        return false;
    }

    result->dice_count = dice_count;
    result->highest_die = focgold_roll_d6_highest(dice_count);
    result->required_to_recover = required;
    result->recovered = result->highest_die >= required;
    result->location = result->recovered ? focgold_roll_bullet_hit_location() :
                                           focgold_hit_chest;
    result->wounds_recovered = result->recovered ? 1 : 0;

    return true;
}
