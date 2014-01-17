#define DEFINE_VARIABLES
#include <init.h>
#include <math.h>

void advance(double x,double y[],double dydx[], double yout[]){

  int i2,j;
 for(i2=0; i2 <=5000; i2++){
   x = i2 * h;
   derivs(x,y,dydx);
   rk4(y,dydx,n,x,h,yout,derivs);
   for(j=0; j<n; j++){y[j]=yout[j];}
   if(fabs(y[0])>100){break;}
  }

}
