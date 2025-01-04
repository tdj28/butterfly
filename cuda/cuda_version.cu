#include <cuda_runtime.h>
#include <stdio.h>
#include <math.h>

// Device constants
__constant__ float d_a;
__constant__ float d_b;
__constant__ float d_c;
__constant__ float d_h;

// Device functions
__device__ void derivs(double x, double y[], double dydx[]) {
    dydx[0] = (-y[1] - y[2]);
    dydx[1] = (y[0] + d_a * y[1]);
    dydx[2] = (d_b + y[2] * (y[0] - d_c));
}

__device__ void rk4_step(double y[], double dydx[], int n, double x, double h, double yout[],
                        void (*derivs)(double, double [], double [])) {
    double xh, hh, h6;
    double dym[3], dyt[3], yt[3];

    hh = h * 0.5;
    h6 = h / 6.0;
    xh = x + hh;

    for (int i = 0; i < n; i++) 
        yt[i] = y[i] + hh * dydx[i];
    derivs(xh, yt, dyt);
    
    for (int i = 0; i < n; i++) 
        yt[i] = y[i] + hh * dyt[i];
    derivs(xh, yt, dym);
    
    for (int i = 0; i < n; i++) {
        yt[i] = y[i] + h * dym[i];
        dym[i] += dyt[i];
    }
    
    derivs(x + h, yt, dyt);
    for (int i = 0; i < n; i++)
        yout[i] = y[i] + h6 * (dydx[i] + dyt[i] + 2.0 * dym[i]);
}

__device__ void advance(double *x, double y[], double dydx[], double yout[]) {
    for(int i2 = 0; i2 <= 5000; i2++) {
        *x = i2 * d_h;
        derivs(*x, y, dydx);
        rk4_step(y, dydx, 3, *x, d_h, yout, derivs);
        for(int j = 0; j < 3; j++) {
            y[j] = yout[j];
        }
        if(fabs(y[0]) > 100) break;
    }
}

__device__ void advancem(double *x, double y[], double dydx[], double yout[], double *gxmin, double *gxmax) {
    double fixedx = d_c/2 - sqrt(d_c*d_c - 4 * d_a * d_b)/2;
    *gxmax = -100000;
    *gxmin = 1000000;
    
    for(int i2 = 0; i2 <= 10000; i2++) {
        *x = i2 * d_h;
        derivs(*x, y, dydx);
        rk4_step(y, dydx, 3, *x, d_h, yout, derivs);
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

__device__ void poincare(double *x, double y[], double dydx[], double yout[], bool processflag) {
    double y0 = 4;
    double fixedx = d_c/2 - sqrt(d_c*d_c - 4 * d_a * d_b)/2;
    double fixedy = -d_c/(2* d_a) + sqrt(d_c*d_c - 4 * d_a * d_b)/(2*d_a);
    bool recflag = false;
    bool poinflag = false;
    bool runloop = true;
    
    *x = 0;
    while(runloop) {
        *x = *x + d_h;
        derivs(*x, y, dydx);
        rk4_step(y, dydx, 3, *x, d_h, yout, derivs);
        
        for(int j = 0; j < 3; j++) {
            y[j] = yout[j];
        }
        
        if(fabs(y[0]) > 100) break;
        
        if(!poinflag) {
            if(((y0-fixedy)*(y[1]-fixedy) < 0) && (y[0] < fixedx)) {
                poinflag = true;
            }
        }
        
        if(poinflag) {
            runloop = false;
        }
        
        y0 = y[1];
    }
}

__global__ void compute_periods(double *y_init, int *periods, float *params, int param_count) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= param_count) return;
    
    // Set parameter values for this thread
    float aa = params[idx*2];    // a value
    float cc = params[idx*2+1];  // c value
    
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
    advance(&x, y, dydx, yout);
    
    // Get width of x on left side
    advancem(&x, y, dydx, yout, &gxmin, &gxmax);
    
    // First period detection
    for(int n = 0; n <= 10; n++) {
        poincare(&x, y, dydx, yout, false);
        trail[10-n] = y[0];
    }
    
    double width = gxmax - gxmin;
    int period = 0;
    
    poincare(&x, y, dydx, yout, false);
    for(int n = 0; n <= 10; n++) {
        double close = fabs(trail[10-n] - y[0])/width;
        if(close < 0.003) {
            period = 10-n+1;
            break;
        }
    }
    
    // Confirm period with second pass
    advance(&x, y, dydx, yout);
    advancem(&x, y, dydx, yout, &gxmin, &gxmax);
    
    for(int n = 0; n <= 10; n++) {
        poincare(&x, y, dydx, yout, false);
        trail[10-n] = y[0];
    }
    
    width = gxmax - gxmin;
    int period2 = 0;
    
    poincare(&x, y, dydx, yout, false);
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

void launch_cuda_computation(const char* filename, double *y_init, float amin, float amax, 
                           float cmin, float cmax, int res, float b_val) {
    int param_count = res * res;
    
    // Allocate device memory
    double *d_y_init;
    int *d_periods, *h_periods;
    float *d_params, *h_params;
    
    cudaMalloc(&d_y_init, 3 * sizeof(double));
    cudaMalloc(&d_periods, param_count * sizeof(int));
    cudaMalloc(&d_params, param_count * 2 * sizeof(float));
    
    h_periods = (int*)malloc(param_count * sizeof(int));
    h_params = (float*)malloc(param_count * 2 * sizeof(float));
    
    // Copy initial conditions to device
    cudaMemcpy(d_y_init, y_init, 3 * sizeof(double), cudaMemcpyHostToDevice);
    
    // Set constants
    float h_val = 0.01f;
    cudaMemcpyToSymbol(d_h, &h_val, sizeof(float));
    cudaMemcpyToSymbol(d_b, &b_val, sizeof(float));
    
    // Generate parameter combinations
    float adiff = (amax - amin) / (res - 1);
    float cdiff = (cmax - cmin) / (res - 1);
    
    int ii = 0, jj = 0;
    for (int i = 0; i < param_count; i++) {
        h_params[i*2] = amin + adiff * (1.0f * ii / (1.0f * res));
        h_params[i*2+1] = cmin + cdiff * (1.0f * jj / (1.0f * res));
        
        jj++;
        if(jj == res) {
            jj = 0;
            ii++;
        }
    }
    
    // Copy parameters to device
    cudaMemcpy(d_params, h_params, param_count * 2 * sizeof(float), cudaMemcpyHostToDevice);
    
    // Launch kernel
    int threadsPerBlock = 256;
    int blocks = (param_count + threadsPerBlock - 1) / threadsPerBlock;
    compute_periods<<<blocks, threadsPerBlock>>>(d_y_init, d_periods, d_params, param_count);
    
    // Copy results back
    cudaMemcpy(h_periods, d_periods, param_count * sizeof(int), cudaMemcpyDeviceToHost);
    
    // Write results to file
    FILE *fp = fopen(filename, "w");
    for (int i = 0; i < param_count; i++) {
        fprintf(fp, "%d %f %f %f %d\n", i % res, h_params[i*2], b_val, h_params[i*2+1], h_periods[i]);
    }
    fclose(fp);
    
    // Cleanup
    cudaFree(d_y_init);
    cudaFree(d_periods);
    cudaFree(d_params);
    free(h_periods);
    free(h_params);
}

int main(int argc, char *argv[]) {
    if (argc != 6) {
        printf("Usage: %s <amin> <amax> <b> <cmin> <cmax>\n", argv[0]);
        return 1;
    }

    float amin = atof(argv[1]);
    float amax = atof(argv[2]);
    float b_val = atof(argv[3]);
    float cmin = atof(argv[4]);
    float cmax = atof(argv[5]);
    
    // Initial conditions (same as original)
    double y_init[3] = {-12.0, 1.13, 0.34};
    
    // Resolution (same as original)
    int res = 500;
    
    // Create output filename
    char filename[30];
    sprintf(filename, "ti_%s_%s_%s_%s_%s", argv[1], argv[2], argv[3], argv[4], argv[5]);
    
    // Launch computation
    launch_cuda_computation(filename, y_init, amin, amax, cmin, cmax, res, b_val);
    
    return 0;
}