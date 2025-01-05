#include "cuda_defs.cuh"

#define MAX_INTERSECTIONS 200
__device__ void poincare(double *x, double y[], double dydx[], double yout[], bool processflag,
                        double h, double a, double b, double c) {
    double y0 = 4.0;  // Match MPI initial value exactly
    double xx[MAX_INTERSECTIONS];
    double xxp[MAX_INTERSECTIONS];
    
    // Fixed point calculation matching MPI exactly
    double fixedx = c/2.0 - sqrt(c*c - 4.0 * a * b)/2.0;
    double fixedy = -c/(2.0 * a) + sqrt(c*c - 4.0 * a * b)/(2.0 * a);
    
    bool recflag = false;
    bool poinflag = false;
    bool runloop = true;
    double xxmin = 10000000.0;
    double xxmax = -10000000.0;
    int count = 0;
    double xpre, ypre, zpre;

    
    *x = 0.0;
    
    while(runloop) {
        *x = *x + h;
        derivs(*x, y, dydx, a, b, c);
        rk4_step(y, dydx, 3, *x, h, yout, a, b, c);
        
        for(int j = 0; j < 3; j++) {
            y[j] = yout[j];
        }
        
        if(fabs(y[0]) > 100.0) break;
        
        // if(!poinflag) {
        //     double y0_diff = y0 - fixedy;
        //     double y1_diff = y[1] - fixedy;
        //     if((y0_diff * y1_diff < 0.0) && (y[0] < fixedx)) {
        //         poinflag = true;
        //     }
        // }
        
        if(!poinflag) {
            // Only accept "stable" looking intersections
            if(((y0-fixedy)*(y[1]-fixedy) < 0) && (y[0]< fixedx) && fabs(y[0]) > 1e-6) {
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
            if(count < MAX_INTERSECTIONS) {
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
    
    // Process data if required
    if(processflag) {
        double dist = xxmax - xxmin;
        double dd = dist/500.0;
        int census[500] = {0};  // Initialize all to 0
        
        // Calculate census as in MPI version
        for(int p = 0; p < count; p++) {
            for(int p2 = 1; p2 <= 500; p2++) {
                double ddmin = xxmin + (p2-1)*dd;
                double ddmax = xxmin + p2*dd;
                if(xx[p] < ddmax && xx[p] > ddmin) {
                    census[p2-1]++;
                }
            }
        }
        
        // Count occupied bins
        int ccount = 0;
        for(int p2 = 0; p2 < 500; p2++) {
            if(census[p2] > 0) {
                ccount++;
            }
        }
        
        // Calculate percentage and adjust for period 1 orbits
        double percentage = 1.0 * ccount / 500.0;
        if(dist < 0.3) {
            percentage = 0.0;
        }
    }
    
    // Return the last intersection point for period calculations
    y[0] = xpre;
}