#include "cuda_defs.cuh"
#include <stdio.h>

__device__ bool check_period(double trail[], double current_x, double width, int n) {
    double close = fabs(trail[10-n] - current_x)/width;
    if (threadIdx.x == 0 && blockIdx.x == 0) {
        printf("Check period n=%d: trail=%f current=%f diff=%f width=%f close=%f threshold=%f\n",
               n, trail[10-n], current_x, fabs(trail[10-n] - current_x), width, close, 0.003);
    }
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
    double gxmin, gxmax;
    
    // Initialize state
    y[0] = y_init[0];
    y[1] = y_init[1];
    y[2] = y_init[2];
    
    if (threadIdx.x == 0 && blockIdx.x == 0) {
        printf("\nStarting first pass for a=%f c=%f\n", thread_a, thread_c);
    }
    
    // First pass
    advance(&x, y, dydx, yout, h_val, thread_a, b_val, thread_c);
    advancem(&x, y, dydx, yout, &gxmin, &gxmax, h_val, thread_a, b_val, thread_c);
    
    // Build trail
    for(int n = 0; n <= 10; n++) {
        poincare(&x, y, dydx, yout, false, h_val, thread_a, b_val, thread_c);
        trail[10-n] = y[0];
        if (threadIdx.x == 0 && blockIdx.x == 0) {
            printf("First pass trail[%d] = %f\n", 10-n, y[0]);
        }
    }
    
    double width = gxmax - gxmin;
    int period = 0;
    
    // Get one more intersection to check against trail
    poincare(&x, y, dydx, yout, false, h_val, thread_a, b_val, thread_c);
    double check_x = y[0];
    
    if (threadIdx.x == 0 && blockIdx.x == 0) {
        printf("First pass check point = %f\n", check_x);
    }
    
    // Check for periods
    for(int n = 0; n <= 10; n++) {
        if(check_period(trail, check_x, width, n)) {
            period = 10-n+1;
            if (threadIdx.x == 0 && blockIdx.x == 0) {
                printf("Found first period: %d\n", period);
            }
            break;
        }
    }
    
    if (threadIdx.x == 0 && blockIdx.x == 0) {
        printf("\nStarting second pass\n");
    }
    
    // Second pass to confirm
    advance(&x, y, dydx, yout, h_val, thread_a, b_val, thread_c);
    advancem(&x, y, dydx, yout, &gxmin, &gxmax, h_val, thread_a, b_val, thread_c);
    
    for(int n = 0; n <= 10; n++) {
        poincare(&x, y, dydx, yout, false, h_val, thread_a, b_val, thread_c);
        trail[10-n] = y[0];
        if (threadIdx.x == 0 && blockIdx.x == 0) {
            printf("Second pass trail[%d] = %f\n", 10-n, y[0]);
        }
    }
    
    width = gxmax - gxmin;
    int period2 = 0;
    
    poincare(&x, y, dydx, yout, false, h_val, thread_a, b_val, thread_c);
    check_x = y[0];
    
    if (threadIdx.x == 0 && blockIdx.x == 0) {
        printf("Second pass check point = %f\n", check_x);
    }
    
    for(int n = 0; n <= 10; n++) {
        if(check_period(trail, check_x, width, n)) {
            period2 = 10-n+1;
            if (threadIdx.x == 0 && blockIdx.x == 0) {
                printf("Found second period: %d\n", period2);
            }
            break;
        }
    }
    
    if(period != period2) {
        if (threadIdx.x == 0 && blockIdx.x == 0) {
            printf("Periods don't match! %d vs %d\n", period, period2);
        }
        period = 0;
    }
    
    periods[idx] = period;
}