#define DEFINE_VARIABLES
#include <init.h>


void derivs(double x,double y[],double dydx[]){ 

   dydx[0] = (-y[1] -y[2]);
   dydx[1] = (y[0] + a*y[1]);
   dydx[2] = (b + y[2]*(y[0]-c));
  
 } 
