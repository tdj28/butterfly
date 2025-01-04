#include <init.h>
void startup(int my_rank, int size){

  MPI_Init(0,0);
  //MPI_Init(&argc, &argv); /*START MPI */
 /*DETERMINE RANK OF THIS PROCESSOR*/
 MPI_Comm_rank(MPI_COMM_WORLD, &my_rank); 
 /*DETERMINE TOTAL NUMBER OF PROCESSORS*/
 MPI_Comm_size(MPI_COMM_WORLD, &size);
}
