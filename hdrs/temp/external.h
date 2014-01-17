/*
** This header must not contain header guards (like <assert.h> must not).
** Each time it is invoked, it redefines the macros EXTERN and INITIALIZER
** based on whether macro DEFINE_VARIABLES is currently defined.
*/
#undef EXTERN
#undef INITIALIZER

#ifdef DEFINE_VARIABLES
#define EXTERN                  extern
#define INITIALIZER(...)        /* nothing */
#else
#define EXTERN                  /* nothing */
#define INITIALIZER(...)        = __VA_ARGS__
#endif /* DEFINE_VARIABLES */

// See http://stackoverflow.com/questions/1433204/how-do-i-share-a-variable-between-source-files-in-c-with-extern-but-how
