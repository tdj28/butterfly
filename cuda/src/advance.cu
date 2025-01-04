#include "cuda_defs.cuh"

__device__ void advance(double *x, double y[], double dydx[], double yout[], float h,
                       double a, double b, double c) {

    for(int i2 = 0; i2 <= 5000; i2++) {
        *x = i2 * h;
        derivs(*x, y, dydx, a, b, c);
        rk4_step(y, dydx, 3, *x, h, yout, a, b, c);
        for(int j = 0; j < 3; j++) {
            y[j] = yout[j];
        }
        if(fabs(y[0]) > 100) break;
    }
}