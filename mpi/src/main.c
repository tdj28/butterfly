#include <init.h>
#include <stdlib.h>
#include <stdio.h>
#include <math.h>

int main(int argc, char *argv[])
{

 bool  processflag=false; //More than one poincare intersection?   

 int size;

 MPI_Init(&argc, &argv); /*START MPI */
 /*DETERMINE RANK OF THIS PROCESSOR*/
 MPI_Comm_rank(MPI_COMM_WORLD, &my_rank); 
 /*DETERMINE TOTAL NUMBER OF PROCESSORS*/
 MPI_Comm_size(MPI_COMM_WORLD, &size);

 //printf("Accounting for all processors...\n");
checkin(my_rank,size);

 FILE *fp0; 
 if(my_rank==0){
       char filename [ 30 ];
      sprintf(filename, "ti_%s_%s_%s_%s_%s",argv[1],argv[2],argv[3],argv[4],argv[5] );
   // printf("Accessing output file...\n");
      fp0=fopen(filename,"w");printf(":MAIN:\n");
 }

 // FILE *fp0; 
 // if (my_rank == 0) {}
 
 float amin,amax,cmin,cmax,adiff,cdiff;
 amin = atof(argv[1]);
 amax = atof(argv[2]);
 b = atof(argv[3]); 
 cmin = atof(argv[4]);
 cmax = atof(argv[5]);
 
 adiff=amax-amin;
 cdiff=cmax-cmin;
   



 float aa,bb,cc;
 int ii=0;
 // printf("Beginning loop...\n");
 int res=500;
 while(ii<res){
   //   printf("In loop\n");
   
   //x=(double*) malloc (n*sizeof(double)); 
    y=(double*) malloc (n*sizeof(double)); 
   dydx=(double*) malloc (n*sizeof(double)); 
    yout=(double*) malloc (n*sizeof(double)); 
   y[0]=-12.0; y[1]=1.13; y[2]=0.34;



 int partner;
 if (my_rank ==0) {
            aa=amin + adiff*(1.0*ii/(1.0*res));
            cc=cmin + cdiff*(1.0*jj/(1.0*res));
            jj++;
            if(jj==res){jj=0; ii++;}
            a=aa;
            c=cc;
	    //  printf("STATE: %d %f %f %f\n",my_rank,a,b,c); 
       for (partner = 1; partner < size; partner++){
                aa=amin + adiff*(1.0*ii/(1.0*res));
		cc=cmin + cdiff*(1.0*jj/(1.0*res));
		//avec[vcount] = aa;
		//		cvec[vcount] = cc; 
		//		perc[vcount] = 0.0;
		//		tag = 1000*ii + jj;
		//		tvec[vcount] = tag;
		MPI_Send(&aa, 1, MPI_FLOAT, partner,1,MPI_COMM_WORLD);
                MPI_Send(&cc, 1, MPI_FLOAT, partner,1,MPI_COMM_WORLD);
                jj++;
		if(jj==res){jj=0; ii++; printf("Moving to %i\n",ii);}
    }///ENDS VCOUNT
    }/// ENDS EXECUTIVE LOOP
  else
    {
        MPI_Recv(&aa, 1, MPI_FLOAT, 0, 1, MPI_COMM_WORLD, &stat);
        MPI_Recv(&cc, 1, MPI_FLOAT, 0, 1, MPI_COMM_WORLD, &stat);
    }


  ///////////////////////////////////////////////////////////////////////
  // DEBUG CODE

  double trail[11];  // Array to store intersection points
  double close;      // For period checking
  bool debug;        // For debug printing

  if(my_rank > 0) {
    a = aa;
    c = cc;
  }

  // Add debug condition

  const double EPSILON = 1e-8;  // More permissive tolerance
  printf("initial params: (%f, %f, %f)\n", a, b, c);
  debug = (fabs(a - 0.1) < EPSILON && 
          fabs(b - 0.2) < EPSILON && 
          fabs(c - 5.0) < EPSILON);
  printf("Debug values: a=%20.15f, b=%20.15f, c=%20.15f\n", a, b, c);
  printf("Debug: %d (differences: %e, %e, %e)\n", debug, 
       fabs(a - 0.1), fabs(b - 0.2), fabs(c - 5.0));
  printf("Debug: %d\n", debug);
  if(debug) printf("\nMPI Initial conditions: (%f, %f, %f)\n", y[0], y[1], y[2]);

  // Clear transients, get on attractor
  advance(x,y,dydx,yout);
  if(debug) printf("After advance: (%f, %f, %f)\n", y[0], y[1], y[2]);

  advancem(x,y,dydx,yout);
  if(debug) printf("After advancem: gxmin=%f, gxmax=%f\n", gxmin, gxmax);

  if(debug) printf("\nBuilding trail array:\n");
  for(n=0; n<=10; n++){
      poincare(x,y,dydx,yout,processflag);
      trail[10-n]=y[0];
      if(debug) printf("Trail[%d] = %f\n", 10-n, trail[10-n]);
  }

  float width=gxmax-gxmin;
  if(debug) printf("\nWidth for normalization: %f\n", width);

  poincare(x,y,dydx,yout,processflag);
  if(debug) printf("Check point: %f\n", y[0]);

  if(debug) printf("\nChecking periods:\n");
  period=0;
  for(n=0; n<=10; n++){
      close = fabs(trail[10-n]-y[0])/width;
      if(debug) printf("n=%d: comparing %f to %f (close=%f)\n", 
                      n, trail[10-n], y[0], close);
      if(close<0.003){
          period = 10-n+1;
          if(debug) printf("Found period: %d\n", period);
          break;
      }
  }

  // if(my_rank > 0){  a =aa; c  = cc;}



  // //Clear transients, get on attractor
  //  advance(x,y,dydx,yout);
  //  //Assuming we are on attractor, get width of x on left side
  //  advancem(x,y,dydx,yout);
  //  //printf("xmin xmax %f %f\n",gxmin,gxmax);
  //  //printf("Poin start\n");
  //  int n;
  //  double trail[11];
  //  for(n=0; n<=10; n++){
  //    poincare(x,y,dydx,yout,processflag);
  //    trail[10-n]=y[0];
  //                     }
  //  float width=gxmax-gxmin;
  //  float close;
 

  //  poincare(x,y,dydx,yout,processflag);
  //  period=0;
  //  for(n=0; n<=10; n++){
  //     close = fabs(trail[10-n]-y[0])/width;
  //     if(close<0.003){period = 10-n+1;}// printf("%i %f\n",period,close);}
  //  }

  ///////////////////////////////////////////////////////////////////////
  ///////////////////////////////////////////////////////////////////////

   /// Now repeat to confirm


           advance(x,y,dydx,yout);
   //Assuming we are on attractor, get width of x on left side
   advancem(x,y,dydx,yout);
   //printf("xmin xmax %f %f\n",gxmin,gxmax);
   //printf("Poin start\n");
   //   int n;
   //   double trail[11];
   for(n=0; n<=10; n++){
     poincare(x,y,dydx,yout,processflag);
     trail[10-n]=y[0];
                      }
   width=gxmax-gxmin;
   //float close;
 

   poincare(x,y,dydx,yout,processflag);
   period2=0;
   for(n=0; n<=10; n++){
      close = fabs(trail[10-n]-y[0])/width;
      if(close<0.003){period2 = 10-n+1;}// printf("%i %f\n",period,close);}
   }
            
   if(period!=period2){period=0;}

   //printf("Poin end\n");
   
   ///////////////////////////////////////////////////////////////////////
   /////////////////// SEND IT BACK TO ROOT AND PRINT OUT ////////////////
   ///////////////////////////////////////////////////////////////////////  
   // printf("Sennding back\n");
   //int partner;
   if(my_rank==0){  
    //  printf("check me\n");
    fprintf(fp0,"%d %f %f %f %i\n",my_rank,a,b,c, period);
     //     printf("FINAL: %d %f\n",my_rank, percentage);
     for (partner = 1; partner < size; partner++){
       //    MPI_Recv(&y[0], 1, MPI_FLOAT, partner, 1, MPI_COMM_WORLD, &stat);
       //        MPI_Recv(&y[1], 1, MPI_FLOAT, partner, 1, MPI_COMM_WORLD, &stat);
       //	MPI_Recv(&y[2], 1, MPI_FLOAT, partner, 1, MPI_COMM_WORLD, &stat);
        MPI_Recv(&period, 1, MPI_INT, partner, 1, MPI_COMM_WORLD, &stat);
        MPI_Recv(&aa, 1, MPI_FLOAT, partner, 2, MPI_COMM_WORLD, &stat);
        MPI_Recv(&cc, 1, MPI_FLOAT, partner, 3, MPI_COMM_WORLD, &stat);
        fprintf(fp0,"%d %f %f %f %i\n",partner,aa,b,cc, period);
     }
   }
   else
    {
      //  MPI_Send(&y[0], 1, MPI_FLOAT, 0,1,MPI_COMM_WORLD);
      //      MPI_Send(&y[1], 1, MPI_FLOAT, 0,1,MPI_COMM_WORLD);
      //      MPI_Send(&y[2], 1, MPI_FLOAT, 0,1,MPI_COMM_WORLD);
      MPI_Send(&period, 1, MPI_FLOAT, 0, 1,MPI_COMM_WORLD);
      MPI_Send(&aa, 1, MPI_FLOAT, 0,2,MPI_COMM_WORLD);
      MPI_Send(&cc, 1, MPI_FLOAT, 0,3,MPI_COMM_WORLD);
    }        
   //   printf("Done sending back\n");
  //////////////////////////////////////////////////////////////////////////
  //////////////////////////////////////////////////////////////////////////
  ////////////////////////////////////////////////////////////////////////// 
 
  
}

   






 /////////////////////////////////////////////////////////////////
 //////////////////////////////////
 /////////////////
 ////////
 ////
 //
   free(y);
   free(dydx); 
   free(yout);


}
