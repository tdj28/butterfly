#include "cuda_defs.cuh"
#include <stdio.h>

void launch_cuda_computation(const char* filename, 
                           double *y_init,
                           double amin,     // Change to double
                           double amax,     // Change to double
                           double cmin,     // Change to double
                           double cmax,     // Change to double
                           int res,
                           double b_val)    // Change to double 
                           {
    int param_count = res * res;
    
    // Allocate device memory
    double *d_y_init;
    int *d_periods, *h_periods;
    double *d_params, *h_params;  // Changed to double
    
    cudaMalloc(&d_y_init, 3 * sizeof(double));
    cudaMalloc(&d_periods, param_count * sizeof(int));
    cudaMalloc(&d_params, param_count * 2 * sizeof(double));  // Changed to double
    
    h_periods = (int*)malloc(param_count * sizeof(int));
    h_params = (double*)malloc(param_count * 2 * sizeof(double));  // Changed to double
    
    cudaMemcpy(d_y_init, y_init, 3 * sizeof(double), cudaMemcpyHostToDevice);
    
    double h_val = 0.01f;
    
    // Match original MPI parameter generation exactly
    double adiff = amax - amin;  // Changed to double
    double cdiff = cmax - cmin;  // Changed to double
    
    // Generate parameters using double arithmetic exactly as MPI does
    for (int ii = 0; ii < res; ii++) {
        for (int jj = 0; jj < res; jj++) {
            int idx = ii * res + jj;
            // Use exact MPI arithmetic
            h_params[idx*2] = (double)amin + ((double)adiff * ((double)ii / (double)res));
            h_params[idx*2+1] = (double)cmin + ((double)cdiff * ((double)jj / (double)res));
        }
    }

    
    cudaMemcpy(d_params, h_params, param_count * 2 * sizeof(double), cudaMemcpyHostToDevice);
    
    int threadsPerBlock = 256;
    int blocks = (param_count + threadsPerBlock - 1) / threadsPerBlock;
    compute_periods<<<blocks, threadsPerBlock>>>(d_y_init, d_periods, d_params, 
                                               (double)b_val, h_val, param_count);  // Cast b_val to double
    
    // Check for errors
    cudaError_t err = cudaGetLastError();
    if (err != cudaSuccess) {
        printf("Kernel launch error: %s\n", cudaGetErrorString(err));
        return;
    }
    
    // Wait for GPU to finish
    cudaDeviceSynchronize();
    
    // Copy results back
    cudaMemcpy(h_periods, d_periods, param_count * sizeof(int), cudaMemcpyDeviceToHost);
    
    // Write results to file using the same format as original
    FILE *fp = fopen(filename, "w");
    if (fp == NULL) {
        printf("Error opening file %s\n", filename);
        return;
    }
    
    // Fixed output ordering to match MPI
    for (int i = 0; i < param_count; i++) {
        int jj = i % res;  // x-index comes from column (jj) like MPI
        fprintf(fp, "%d %f %f %f %d\n", 
                jj,                    // Use jj as x-index like MPI
                h_params[i*2],         // a value
                b_val,                 // b value
                h_params[i*2+1],       // c value
                h_periods[i]);         // period
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

    double amin = atof(argv[1]);
    double amax = atof(argv[2]);
    double b_val = atof(argv[3]);
    double cmin = atof(argv[4]);
    double cmax = atof(argv[5]);
    
    double y_init[3] = {-12.0, 1.13, 0.34};
    int res = 500;
    
    char filename[30];
    sprintf(filename, "ti_%s_%s_%s_%s_%s", argv[1], argv[2], argv[3], argv[4], argv[5]);
    
    launch_cuda_computation(filename, y_init, amin, amax, cmin, cmax, res, b_val);
    
    return 0;
}