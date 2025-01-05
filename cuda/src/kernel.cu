#include "cuda_defs.cuh"
#include <stdio.h>

__device__ bool check_period(double trail[], double current_x, double width, int n) {
    double close = fabs(trail[10-n] - current_x)/width;
    return (close < 0.003);
}

__global__ void compute_periods(double *y_init, int *periods, double *params, double b_val, float h_val,
                              int param_count) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= param_count) return;

    double thread_a = params[idx*2];
    double thread_c = params[idx*2+1];
    
    // Local variables
    double y[3], dydx[3], yout[3];
    double x = 0.0;
    double trail[11];
    double gxmin = 1000000.0, gxmax = -100000.0;
    
    // Initialize state exactly as MPI version
    y[0] = y_init[0];
    y[1] = y_init[1];
    y[2] = y_init[2];
    
    // First pass
    // Clear transients and get on attractor
    advance(&x, y, dydx, yout, h_val, thread_a, b_val, thread_c);
    
    // Get width of x on left side
    advancem(&x, y, dydx, yout, &gxmin, &gxmax, h_val, thread_a, b_val, thread_c);
    
    // Build trail array - key fix here: store points in same order as MPI
    for(int n = 0; n <= 10; n++) {
        poincare(&x, y, dydx, yout, false, h_val, thread_a, b_val, thread_c);
        trail[10-n] = y[0];
    }
    
    double width = gxmax - gxmin;
    int period = 0;
    
    // Get next intersection
    poincare(&x, y, dydx, yout, false, h_val, thread_a, b_val, thread_c);
    double check_x = y[0];
    
    // Check periods using width-normalized distance
    for(int n = 0; n <= 10; n++) {
        if(check_period(trail, check_x, width, n)) {
            period = 10-n+1;
            break;
        }
    }
    
    // Second pass to confirm
    x = 0.0;
    y[0] = y_init[0];
    y[1] = y_init[1];
    y[2] = y_init[2];
    
    advance(&x, y, dydx, yout, h_val, thread_a, b_val, thread_c);
    advancem(&x, y, dydx, yout, &gxmin, &gxmax, h_val, thread_a, b_val, thread_c);
    
    for(int n = 0; n <= 10; n++) {
        poincare(&x, y, dydx, yout, false, h_val, thread_a, b_val, thread_c);
        trail[10-n] = y[0];
    }
    
    width = gxmax - gxmin;
    int period2 = 0;
    
    poincare(&x, y, dydx, yout, false, h_val, thread_a, b_val, thread_c);
    check_x = y[0];
    
    for(int n = 0; n <= 10; n++) {
        if(check_period(trail, check_x, width, n)) {
            period2 = 10-n+1;
            break;
        }
    }
    
    // Key fix: Match MPI version's period validation
    if(period != period2) {
        period = 0;
    }
    
    periods[idx] = period;
}
