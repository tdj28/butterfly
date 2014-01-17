#ifndef DEFINE_H_INCLUDED
#define DEFINE_H_INCLUDED


#ifndef MYBOOLEAN_H
#define MYBOOLEAN_H

#define false 0
#define true 1
typedef int bool; // or #define bool int

#endif

extern void derivs(double,double [],double []);

extern void rk4(double [], double [], int, double, double, double [], void (*derivs)(double, double [], double []));

extern void poincare(double,double [],double [], double [], bool);

extern void advance(double,double [],double [], double []);

extern void advancem(double,double [],double [], double []);

extern void checkin(int, int);


//extern void startup(int my_rank, int size);



#endif
