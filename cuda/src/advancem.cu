#include "cuda_defs.cuh"

// 2. Fixed point calculations
__device__ void compute_fixed_points(double a, double b, double c, 
                                   double *fixedx, double *fixedy) {
    // Match MPI fixed point calculations exactly:
    *fixedx = c/2.0 - sqrt(c*c - 4.0 * a * b)/2.0;
    *fixedy = -c/(2.0 * a) + sqrt(c*c - 4.0 * a * b)/(2.0 * a);
}

__device__ void advancem(double *x, double y[], double dydx[], double yout[], double *gxmin, 
                        double *gxmax, float h, double a, double b, double c) {
    double fixedx;
    double fixedy;
    compute_fixed_points(a, b, c, &fixedx, &fixedy);
    
    *gxmax = -100000.0;  // Match MPI initial values
    *gxmin = 1000000.0;

    for(int i2 = 0; i2 <= 10000; i2++) {
        *x = i2 * h;
        derivs(*x, y, dydx, a, b, c);
        rk4_step(y, dydx, 3, *x, h, yout, a, b, c);
        for(int j = 0; j < 3; j++) {
            y[j] = yout[j];
            if(y[0] < fixedx) {
                if(y[0] < *gxmin) *gxmin = y[0];
                if(y[0] > *gxmax) *gxmax = y[0];
            }
        }
        if(fabs(y[0]) > 100) break;
    }
}