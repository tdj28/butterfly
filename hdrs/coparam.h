#ifndef COPARAM_H_INCLUDED
#define COPARAM_H_INCLUDED

#include <mpi.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>


void advance(double x,double y[],double dydx[], double yout[]);
void advancem(double x,double y[],double dydx[], double yout[]);
void checkin(int my_rank, int size);
void derivs(double x,double y[],double dydx[]);
void poincare(double x,double y[],double dydx[], double yout[], bool processflag);
void rk4(double y[], double dydx[], int n, double x, double h, double yout[],
	 void (*derivs)(double, double [], double []));
void startup(int my_rank, int size);





#ifdef DEFINE_VARIABLES
#define EXTERN /* nothing */
#else
#define EXTERN extern
#endif /* DEFINE_VARIABLES */

EXTERN float a;
EXTERN float b;
EXTERN float c;
EXTERN int n;
EXTERN float h;
EXTERN float percentage;
//float aa,cc;
EXTERN int jj;
//float aa,cc;
EXTERN double gxmax,gxmin;
EXTERN int period,period2;

EXTERN int my_rank; 
EXTERN MPI_Status stat;
EXTERN double *dydx; double *yout;
EXTERN double x; double *y;
#endif
