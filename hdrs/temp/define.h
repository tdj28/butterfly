#ifndef DEFINE_H_INCLUDED
#define DEFINE_H_INCLUDED


//#ifndef MYBOOLEAN_H
//#define MYBOOLEAN_H

//#define false 0
//#define true 1
//typedef int bool; // or #define bool int

//#endif

extern void derivs(double xx,double yy[],double dydxx[]);

extern void rk4(double yy[], double dydx[], int nn, double xx, double hh, double youtt[], void (*derivs)(double, double [], double []));

extern void poincare(double xx,double yy[],double dydxx[], double youtt[], bool processflag);

extern void advance(double xx,double yy[],double dydxx[], double youtt[]);

extern void advancem(double xx,double yy[],double dydxx[], double youtt[]);

extern void checkin(int my_rankk, int size);


//extern void startup(int my_rank, int size);



#endif
