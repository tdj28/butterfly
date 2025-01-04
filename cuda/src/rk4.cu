#include "cuda_defs.cuh"

__device__ void rk4_step(double y[], double dydx[], int n, double x, double h, double yout[],
                        double a, double b, double c) {
    double xh, hh, h6;
    double dym[3], dyt[3], yt[3];

    hh = h * 0.5;
    h6 = h / 6.0;
    xh = x + hh;

    for (int i = 0; i < n; i++) 
        yt[i] = y[i] + hh * dydx[i];
    derivs(xh, yt, dyt, a, b, c);
    
    for (int i = 0; i < n; i++) 
        yt[i] = y[i] + hh * dyt[i];
    derivs(xh, yt, dym, a, b, c);
    
    for (int i = 0; i < n; i++) {
        yt[i] = y[i] + h * dym[i];
        dym[i] += dyt[i];
    }
    
    derivs(x + h, yt, dyt, a, b, c);
    for (int i = 0; i < n; i++)
        yout[i] = y[i] + h6 * (dydx[i] + dyt[i] + 2.0 * dym[i]);
}

