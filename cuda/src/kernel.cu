#include "cuda_defs.cuh"

__global__ void compute_periods(double *y_init, int *periods, float *params, float b_val, float h_val,
                              int param_count) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= param_count) return;
    
    // Get parameter values for this thread
    float thread_a = params[idx*2];    // a value
    float thread_c = params[idx*2+1];  // c value
    
    // Local variables
    double y[3], dydx[3], yout[3];
    double x = 0.0;
    double trail[11];
    double gxmin, gxmax;
    
    // Initialize state
    y[0] = y_init[0];
    y[1] = y_init[1];
    y[2] = y_init[2];
    
    // Clear transients and get on attractor
    advance(&x, y, dydx, yout, h_val, thread_a, b_val, thread_c);
    
    // Get width of x on left side
    advancem(&x, y, dydx, yout, &gxmin, &gxmax, h_val, thread_a, b_val, thread_c);
    
    // First period detection
    for(int n = 0; n <= 10; n++) {
        poincare(&x, y, dydx, yout, false, h_val, thread_a, b_val, thread_c);
        trail[10-n] = y[0];
    }
    
    double width = gxmax - gxmin;
    int period = 0;
    
    poincare(&x, y, dydx, yout, false, h_val, thread_a, b_val, thread_c);
    for(int n = 0; n <= 10; n++) {
        double close = fabs(trail[10-n] - y[0])/width;
        if(close < 0.003) {
            period = 10-n+1;
            break;
        }
    }
    
    // Confirm period with second pass
    advance(&x, y, dydx, yout, h_val, thread_a, b_val, thread_c);
    advancem(&x, y, dydx, yout, &gxmin, &gxmax, h_val, thread_a, b_val, thread_c);
    
    for(int n = 0; n <= 10; n++) {
        poincare(&x, y, dydx, yout, false, h_val, thread_a, b_val, thread_c);
        trail[10-n] = y[0];
    }
    
    width = gxmax - gxmin;
    int period2 = 0;
    
    poincare(&x, y, dydx, yout, false, h_val, thread_a, b_val, thread_c);
    for(int n = 0; n <= 10; n++) {
        double close = fabs(trail[10-n] - y[0])/width;
        if(close < 0.003) {
            period2 = 10-n+1;
            break;
        }
    }
    
    // If periods don't match, set to 0
    if(period != period2) {
        period = 0;
    }
    
    periods[idx] = period;
}