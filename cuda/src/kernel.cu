#include "cuda_defs.cuh"
#include <stdio.h>

__device__ bool check_period(double trail[], double current_x, double width, int n) {
    double diff = trail[10-n] - current_x;
    double close = fabs(diff)/width;
    return (close < 0.003);
}

// In kernel.cu, modify compute_periods:

__global__ void compute_periods(double *y_init, 
                              int *periods,
                              double *params,
                              double b_val,
                              double h_val,
                              int param_count)
{
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= param_count) return;

    double thread_a = params[idx*2];
    double thread_c = params[idx*2+1];
    
    // Only debug our specific point
    bool debug = (thread_a == 0.1 && b_val == 0.2 && thread_c == 5.0);
    
    // Local variables
    double y[3], dydx[3], yout[3];
    double x = 0.0;
    double trail[11];
    double gxmin = 1000000.0, gxmax = -100000.0;
    
    y[0] = y_init[0];
    y[1] = y_init[1];
    y[2] = y_init[2];
    
    if(debug) printf("\nCUDA Initial conditions: (%f, %f, %f)\n", y[0], y[1], y[2]);
    
    // First pass
    advance(&x, y, dydx, yout, h_val, thread_a, b_val, thread_c);
    if(debug) printf("After advance: (%f, %f, %f)\n", y[0], y[1], y[2]);
    
    advancem(&x, y, dydx, yout, &gxmin, &gxmax, h_val, thread_a, b_val, thread_c);
    if(debug) printf("After advancem: gxmin=%f, gxmax=%f\n", gxmin, gxmax);
    
    // Build trail array
    if(debug) printf("\nBuilding trail array:\n");
    for(int n = 0; n <= 10; n++) {
        poincare(&x, y, dydx, yout, false, h_val, thread_a, b_val, thread_c);
        trail[10-n] = y[0];
        if(debug) printf("Trail[%d] = %f\n", 10-n, trail[10-n]);
    }
    
    double width = gxmax - gxmin;
    if(debug) printf("\nWidth for normalization: %f\n", width);
    
    // Get next intersection
    poincare(&x, y, dydx, yout, false, h_val, thread_a, b_val, thread_c);
    double check_x = y[0];
    if(debug) printf("Check point: %f\n", check_x);
    
    // Check periods
    if(debug) printf("\nChecking periods:\n");
    int period = 0;
    for(int n = 0; n <= 10; n++) {
        double close = fabs(trail[10-n] - check_x)/width;
        if(debug) printf("n=%d: comparing %f to %f (close=%f)\n", 
                        n, trail[10-n], check_x, close);
        if(close < 0.003) {
            period = 10-n+1;
            if(debug) printf("Found period: %d\n", period);
            break;
        }
    }
    
    periods[idx] = period;
}

// // Update the compute_periods kernel with new validation logic
// __global__ void compute_periods(double *y_init, 
//                               int *periods,
//                               double *params,
//                               double b_val,
//                               double h_val,
//                               int param_count)
// {
//     int idx = blockIdx.x * blockDim.x + threadIdx.x;
//     if (idx >= param_count) return;

//     double thread_a = params[idx*2];
//     double thread_c = params[idx*2+1];
    
//     // Local variables
//     double y[3], dydx[3], yout[3];
//     double x = 0.0;
//     double trail[11];
//     double gxmin = 1000000.0, gxmax = -100000.0;
    
//     // Initialize state
//     y[0] = y_init[0];
//     y[1] = y_init[1];
//     y[2] = y_init[2];
    
//     // First pass
//     advance(&x, y, dydx, yout, h_val, thread_a, b_val, thread_c);
//     advancem(&x, y, dydx, yout, &gxmin, &gxmax, h_val, thread_a, b_val, thread_c);
    
//     for(int n = 0; n <= 10; n++) {
//         poincare(&x, y, dydx, yout, false, h_val, thread_a, b_val, thread_c);
//         trail[10-n] = y[0];
//     }
    
//     double width = gxmax - gxmin;
//     int period_first = 0;
    
//     poincare(&x, y, dydx, yout, false, h_val, thread_a, b_val, thread_c);
//     double check_x = y[0];
    
//     for(int n = 0; n <= 10; n++) {
//         if(check_period(trail, check_x, width, n)) {
//             period_first = 10-n+1;
//             break;
//         }
//     }
    
//     // Second pass - complete reset and rerun
//     x = 0.0;
//     y[0] = y_init[0];
//     y[1] = y_init[1];
//     y[2] = y_init[2];
    
//     advance(&x, y, dydx, yout, h_val, thread_a, b_val, thread_c);
//     advancem(&x, y, dydx, yout, &gxmin, &gxmax, h_val, thread_a, b_val, thread_c);
    
//     for(int n = 0; n <= 10; n++) {
//         poincare(&x, y, dydx, yout, false, h_val, thread_a, b_val, thread_c);
//         trail[10-n] = y[0];
//     }
    
//     width = gxmax - gxmin;
//     int period_second = 0;
    
//     poincare(&x, y, dydx, yout, false, h_val, thread_a, b_val, thread_c);
//     check_x = y[0];
    
//     for(int n = 0; n <= 10; n++) {
//         if(check_period(trail, check_x, width, n)) {
//             period_second = 10-n+1;
//             break;
//         }
//     }
    
//     // MPI-style validation - periods must match exactly
//     if(period_first != period_second) {
//         periods[idx] = 0;
//     } else {
//         periods[idx] = period_first;
//     }
// }