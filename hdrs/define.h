#ifndef DEFINE_H_INCLUDED
#define DEFINE_H_INCLUDED

#ifndef MYBOOLEAN_H
#define MYBOOLEAN_H

#define false 0
#define true 1
typedef int bool;

#endif

// Function declarations
extern void derivs(double, double [], double []);
extern void rk4(double [], double [], int, double, double, double [],
               void (*derivs)(double, double [], double []));
extern void poincare(double, double [], double [], double [], bool);
extern void advance(double, double [], double [], double []);
extern void advancem(double, double [], double [], double []);
extern void checkin(int, int);

#endif /* DEFINE_H_INCLUDED */