#if defined(DEFINE_VARIABLES) && !defined(INIT_H_DEFINITIONS)
#undef INIT_H_INCLUDED
#endif

#ifndef INIT_H_INCLUDED
#define INIT_H_INCLUDED

#include <external.h>   /* Support macros EXTERN and INITIALIZER */
#include <define.h>     /* definitions */


EXTERN int n INITIALIZER(3);
EXTERN float h INITIALIZER(0.01);
EXTERN int jj INITIALIZER(0);
EXTERN float a;
EXTERN float b;
EXTERN float c;
//EXTERN int n;
//EXTERN float h;
EXTERN float percentage;
//float aa,cc;
//EXTERN int jj;
//float aa,cc;
EXTERN double gxmax,gxmin;
EXTERN int period,period2;

EXTERN int my_rank; 
#include <mpi.h>
EXTERN MPI_Status stat;
EXTERN double *dydx; double *yout;
EXTERN double x; double *y;

/* Standard epilogue */
#ifdef DEFINE_VARIABLES
#define INIT_H_DEFINITIONS
#undef DEFINE_VARIABLES     /* Safety first */
#endif /* DEFINE_VARIABLES */

#endif /* INIT_H_INCLUDED */
