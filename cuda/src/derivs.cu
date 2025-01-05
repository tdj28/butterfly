#include "cuda_defs.cuh"

// __device__ void derivs(double x, double y[], double dydx[], double a, double b, double c) {
//     dydx[0] = (-y[1] - y[2]);
//     dydx[1] = (y[0] + a * y[1]);
//     dydx[2] = (b + y[2] * (y[0] - c));
// }

__device__ void derivs(double x, double y[], double dydx[], double a, double b, double c) {
    // Use precise intrinsics for critical calculations
    dydx[0] = __dmul_rn(-1.0, __dadd_rn(y[1], y[2]));  // (-y[1] - y[2])
    dydx[1] = __dadd_rn(y[0], __dmul_rn(a, y[1]));     // (y[0] + a*y[1])
    
    // For the last equation which has more complex terms
    double temp1 = __dmul_rn(y[2], y[0]);               // y[2]*y[0]
    double temp2 = __dmul_rn(y[2], c);                  // y[2]*c
    double temp3 = __dsub_rn(temp1, temp2);             // y[2]*(y[0]-c)
    dydx[2] = __dadd_rn(b, temp3);                      // b + y[2]*(y[0]-c)
}