#define DEFINE_VARIABLES
#include <init.h>
#include <math.h>

void advancem(double x,double y[],double dydx[], double yout[]){

  int i2,j;
  gxmax=-100000;
  gxmin=1000000;
   double fixedx = c/2-sqrt(c*c -4 * a * b)/2;
 for(i2=0; i2 <=10000; i2++){
   x = i2 * h;
   derivs(x,y,dydx);
   rk4(y,dydx,n,x,h,yout,derivs);
   for(j=0; j<n; j++){y[j]=yout[j];if(y[0]<fixedx){ if(y[0]<gxmin){gxmin=y[0];} if(y[0]>gxmax){gxmax=y[0];}}} 
   if(fabs(y[0])>100){break;}

  }

}
