// init.h
#ifndef INIT_H_INCLUDED
#define INIT_H_INCLUDED

#include <mpi.h>
#include <define.h>

// All variables declared as extern
extern int n;
extern float h;
extern int jj;
extern float a;
extern float b;
extern float c;
extern float percentage;
extern double gxmax, gxmin;
extern int period, period2;
extern int my_rank;
extern MPI_Status stat;
extern double *dydx;
extern double *yout;
extern double x;
extern double *y;

#endif /* INIT_H_INCLUDED */