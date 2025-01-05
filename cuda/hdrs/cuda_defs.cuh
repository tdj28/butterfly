// cuda_defs.cuh
#ifndef CUDA_DEFS_CUH
#define CUDA_DEFS_CUH

#include <cuda_runtime.h>

// Device function declarations
__device__ void derivs(double x, double y[], double dydx[], double a, double b, double c);
__device__ void rk4_step(double y[], double dydx[], int n, double x, double h, double yout[],
                        double a, double b, double c);
__device__ void advance(double *x, double y[], double dydx[], double yout[], double h,
                       double a, double b, double c);
__device__ void advancem(double *x, double y[], double dydx[], double yout[], double *gxmin, 
                        double *gxmax, double h, double a, double b, double c);
__device__ void poincare(double *x, double y[], double dydx[], double yout[], bool processflag,
                        double h, double a, double b, double c);

// Kernel declaration
__global__ void compute_periods(double *y_init, int *periods, double *params, double b_val, double h_val, 
                              int param_count);

// Host function declaration
void launch_cuda_computation(const char* filename, double *y_init, double amin, double amax, 
                           double cmin, double cmax, int res, double b_val);

#endif