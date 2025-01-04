#include "cuda_defs.cuh"

__device__ void poincare(double *x, double y[], double dydx[], double yout[], bool processflag,
                        float h, float a, float b, float c) {
    double y0 = 4;
    double fixedx = c/2 - sqrt(c*c - 4 * a * b)/2;
    double fixedy = -c/(2* a) + sqrt(c*c - 4 * a * b)/(2*a);
    bool recflag = false;
    bool poinflag = false;
    bool runloop = true;
    double xxmin = 10000000.0;
    double xxmax = -10000000.0;
    int count = 0;
    double xpre, ypre, zpre;
    
    // Allocate device memory - using shared memory for thread-local arrays
    __shared__ double xx[200];  // Pre-allocate maximum size
    __shared__ double xxp[200];
    
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
            if(count < 200) {  // Prevent buffer overflow
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
            if(processflag && count >= 200) {
                runloop = false;
            }
        }
        
        y0 = y[1];
    }
    
    // Process the data if requested
    if(processflag) {
        double dist = xxmax - xxmin;
        double dd = dist/500;
        int census[500] = {0};
        float percentage = 0.0f;
        
        // Calculate census
        for(int p = 0; p < count; p++) {
            for(int p2 = 1; p2 <= 500; p2++) {
                double ddmin = xxmin + (p2-1)*dd;
                double ddmax = xxmin + p2*dd;
                if(xx[p] < ddmax && xx[p] > ddmin) {
                    census[p2-1]++;
                }
            }
        }
        
        // Calculate percentage of occupied bins
        int ccount = 0;
        for(int p2 = 0; p2 < 500; p2++) {
            if(census[p2] > 0) ccount++;
        }
        
        percentage = 1.0f * ccount/500.0f;
        if(dist < 0.3) percentage = 0.0f;  // Period 1 orbits aren't chaotic
        
        // Store percentage in global memory if needed
        // (would need to add a parameter for this)
    }
}