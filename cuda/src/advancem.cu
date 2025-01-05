#include "cuda_defs.cuh"

// __device__ void compute_fixed_points(double a, double b, double c, 
//                                    double *fixedx, double *fixedy) {
//     // Use parentheses to ensure exact order of operations
//     *fixedx = (c/2.0) - (sqrt((c*c) - (4.0 * a * b))/2.0);
//     *fixedy = (-c/(2.0 * a)) + (sqrt((c*c) - (4.0 * a * b))/(2.0 * a));
// }

__device__ void compute_fixed_points(double a, double b, double c, 
                                   double *fixedx, double *fixedy) {
    double four_ab = __dmul_rn(4.0, __dmul_rn(a, b));
    double c_sq = __dmul_rn(c, c);
    double discriminant = __dsqrt_rn(__dsub_rn(c_sq, four_ab));
    
    *fixedx = __dmul_rn(0.5, __dsub_rn(c, discriminant));
    *fixedy = __dmul_rn(0.5, __ddiv_rn(__dadd_rn(-c, discriminant), a));
}

__device__ void advancem(double *x, double y[], double dydx[], double yout[], 
                        double *gxmin, double *gxmax, double h, double a, double b, double c) {
    double fixedx = c/2 - sqrt(c*c - 4 * a * b)/2;
    
    *gxmax = -100000.0;  // Match MPI initial values exactly
    *gxmin = 1000000.0;

    for(int i2 = 0; i2 <= 10000; i2++) {
        *x = i2 * h;
        derivs(*x, y, dydx, a, b, c);
        rk4_step(y, dydx, 3, *x, h, yout, a, b, c);
        
        // Match MPI version's logic exactly
        for(int j = 0; j < 3; j++) {
            y[j] = yout[j];
            // Only update bounds if we're looking at y[0] and it's less than fixedx
            if(j == 0 && y[0] < fixedx) {
                if(y[0] < *gxmin) *gxmin = y[0];
                if(y[0] > *gxmax) *gxmax = y[0];
            }
        }
        if(fabs(y[0]) > 100) break;
    }
}