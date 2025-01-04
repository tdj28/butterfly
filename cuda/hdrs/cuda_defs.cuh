#ifndef CUDA_DEFS_CUH
#define CUDA_DEFS_CUH

#include <cuda_runtime.h>

// Device function declarations
__device__ void derivs(double x, double y[], double dydx[], float a, float b, float c);
__device__ void rk4_step(double y[], double dydx[], int n, double x, double h, double yout[],
                        float a, float b, float c);
__device__ void advance(double *x, double y[], double dydx[], double yout[], float h,
                       float a, float b, float c);
__device__ void advancem(double *x, double y[], double dydx[], double yout[], double *gxmin, 
                        double *gxmax, float h, float a, float b, float c);
__device__ void poincare(double *x, double y[], double dydx[], double yout[], bool processflag,
                        float h, float a, float b, float c);

// Kernel declaration
__global__ void compute_periods(double *y_init, int *periods, float *params, float b_val, float h_val, 
                              int param_count);

// Host function declarations
void launch_cuda_computation(const char* filename, double *y_init, float amin, float amax, 
                           float cmin, float cmax, int res, float b_val);

#endif