#include <stddef.h>
void *memset(void *p,int v,size_t n){unsigned char *s=p;while(n--)*s++=(unsigned char)v;return p;}
int strcmp(const char *a,const char *b){while(*a && *a==*b){a++;b++;}return (unsigned char)*a-(unsigned char)*b;}
