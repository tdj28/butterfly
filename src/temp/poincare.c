#define DEFINE_VARIABLES
#include <init.h>
#include <stdlib.h>
#include <math.h>



void poincare(double x,double y[],double dydx[], double yout[], bool processflag){

 int i2,j;
 double y0 = 4;
 double fixedx = c/2-sqrt(c*c -4 * a * b)/2;
 double fixedy = -c/(2* a) + sqrt(c*c -4 * a * b)/(2*a);
 bool recflag = false;
 bool poinflag = false;
 bool runloop = true;
 double xxmin = 10000000.0; 
 double xxmax = -10000000.0;
 int count=0;
 double xpre,ypre,zpre;
 double *xx; 
 xx = (double*) malloc (sizeof(double));
 double *xxp; 
 xxp  = (double*) malloc (sizeof(double));

 ////////////////////////////////////////////////////////////
 // for(i2=0; i2<=30000; i2++){
 x=0;
 // printf("IN runloop\n");
 while(runloop){
    
    x = x + h;
    derivs(x,y,dydx);
    rk4(y,dydx,n,x,h,yout,derivs);
    // printf("%f\n",x);
    for(j=0; j<n; j++){y[j]=yout[j];}
    if(fabs(y[0])>100){break;}
    //if(my_rank==0)printf("%f %f %f %f %f %f\n",a,b,c,y[0],y[1],y[2]);
    if(!poinflag){if(  ( (y0-fixedy)*(y[1]-fixedy) < 0) && (y[0]< fixedx) ){ poinflag = true;}} 
    if (poinflag  && !recflag) { 
		       recflag = true; poinflag = false;
                       xpre = y[0]; ypre = y[1]; zpre = y[2];
                       }
   
      if (poinflag && recflag) { 
               xx = (double*) realloc (xx, (count + 1) * sizeof(double));
               xxp = (double*) realloc (xxp, (count + 1) * sizeof(double));
               xx[count]=xpre;
               xxp[count]=y[0];     
               if(xpre<xxmin){xxmin=xpre;}
               if(xpre>xxmax){xxmax=xpre;}
               count++;
	       // printf("count = %i\n",count);
               xpre = y[0]; ypre = y[1]; zpre = y[2]; 
               poinflag=0;
               if(!processflag){runloop = false;}
               if(processflag){if(count==200){runloop = false;}}
      }
      
      y0 = y[1];
                              
 }
 ///////////////////////////////////////////////////////////
 // printf("entering process\n");
 if(processflag){
  int p,p2;
  double dist = xxmax - xxmin;
  double dd = dist/500;
  double ddmin,ddmax;
  int census[500];
  //  float percentage;
  percentage=0.0;

  for(p2=0; p2<500; p2++){census[p2] = 0;}

  for(p=0; p<count; p++){  
    for(p2=1; p2<=500; p2++){     
      ddmin=xxmin + (p2-1)*dd; 
      ddmax=xxmin + p2*dd; 
      if(xx[p] < ddmax && xx[p] > ddmin){census[p2-1]++;}
    }}

  int ccount = 0;
  for(p2=0; p2<500; p2++){if(census[p2] > 0){ccount++;}}
  percentage = 1.0*ccount/500.0;
  if(dist<0.3){percentage = 0.0;}   // Ensure that period 1 orbits aren't seen as chaotic
 }
 // printf("Freeing\n");
 free(xx);
 free(xxp);
 // printf("Done freeing\n");
}
