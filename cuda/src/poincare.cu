#include "cuda_defs.cuh"

__device__ void poincare(double *x, double y[], double dydx[], double yout[], bool processflag,
                        float h, double a, double b, double c) {
    double y0 = 4;
    double fixedx = c/2-sqrt(c*c -4 * a * b)/2;
    double fixedy = -c/(2* a) + sqrt(c*c -4 * a * b)/(2*a);
    bool recflag = false;
    bool poinflag = false;
    bool runloop = true;
    double xxmin = 10000000.0;
    double xxmax = -10000000.0;
    int count = 0;
    double xpre, ypre, zpre;
    
    // Instead of shared memory, use thread-local arrays large enough for all data
    // Since we can't do dynamic allocation in CUDA, pre-allocate max size
    double xx[1000];    // Make arrays bigger than we need to be safe
    double xxp[1000];
    
    *x = 0;
    
    while(runloop) {
        *x = *x + h;
        derivs(*x, y, dydx, a, b, c);
        rk4_step(y, dydx, 3, *x, h, yout, a, b, c);
        
        for(int j = 0; j < 3; j++) {
            y[j] = yout[j];
        }
        
        if(fabs(y[0]) > 100) break;
        
        if(!poinflag) {
            if(((y0-fixedy)*(y[1]-fixedy) < 0) && (y[0] < fixedx)) {
                poinflag = true;
            }
        }
        
        if(poinflag && !recflag) {
            recflag = true;
            poinflag = false;
            xpre = y[0];
            ypre = y[1];
            zpre = y[2];
        }
        
        if(poinflag && recflag) {
            if(count < 1000) {  // Use larger buffer
                xx[count] = xpre;
                xxp[count] = y[0];
                if(xpre < xxmin) xxmin = xpre;
                if(xpre > xxmax) xxmax = xpre;
                count++;
            }
            xpre = y[0];
            ypre = y[1];
            zpre = y[2];
            poinflag = false;
            
            if(!processflag) {
                runloop = false;
            }
            if(processflag) {
                if(count == 200) runloop = false;  // Keep original limit
            }
        }
        
        y0 = y[1];
    }
    
    // Pass back the last intersection point just like MPI version
    y[0] = xpre;
}