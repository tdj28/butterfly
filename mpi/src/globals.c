
// globals.c
#include <init.h>
#include <stddef.h>

// Define all variables here
int n = 3;
float h = 0.01;
int jj = 0;
float a;
float b;
float c;
float percentage;
double gxmax, gxmin;
int period, period2;
int my_rank;
MPI_Status stat;
double *dydx = NULL;
double *yout = NULL;
double x;
double *y = NULL;