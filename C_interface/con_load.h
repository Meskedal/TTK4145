
#include <stdio.h>
#include <string.h>
#define con_load(file, cases)                               \
{                                                           \
    FILE* _f = fopen(file, "r");                            \
    if(_f){                                                 \
        char _line[128] = {0};                              \
        while(fgets(_line, 128, _f)){                       \
            if(!strncmp(_line, "--", 2)){                   \
                char _key[64];                              \
                char _val[64];                              \
                sscanf(_line, "--%s %s", _key, _val);       \
                cases                                       \
            }                                               \
        }                                                   \
    } else {                                                \
        printf("Unable to open config file %s\n", file);    \
    }                                                       \
}


#define con_val(key, var, fmt)                              \
    if(!strcasecmp(_key, key)){                             \
        sscanf(_val, fmt, var);                             \
    }


#define con_enum(key, var, match_cases)                     \
    if(!strcasecmp(_key, key)){                             \
        typeof(*var) _v;                                    \
        match_cases                                         \
        *var = _v;                                          \
    }

#define con_match(id)                                       \
    if(!strcasecmp(_val, #id)){                             \
        _v = id;                                            \
    }
