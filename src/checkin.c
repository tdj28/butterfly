#define DEFINE_VARIABLES
#include <init.h>
#include <stdio.h>
#include <string.h>


void checkin(int my_rank, int size){

  // MPI_Status stat;
 int partner;
 char greeting[100];
 char processor_name[MPI_MAX_PROCESSOR_NAME];
 int name_len;
 MPI_Get_processor_name(processor_name, &name_len);
 sprintf(greeting,"Rank (processor number) %d of %d on server %s checks in\n", my_rank, size,processor_name);
 if (my_rank == 0) printf("BEGIN:\n");

   if (my_rank ==0) {
    fputs(greeting, stdout);
    for (partner = 1; partner < size; partner++){
      
      
      MPI_Recv(greeting, sizeof(greeting), MPI_BYTE, partner, 1, MPI_COMM_WORLD, &stat);
      fputs (greeting, stdout);
      
    }
  }
  else {
    MPI_Send(greeting, strlen(greeting)+1, MPI_BYTE, 0,1,MPI_COMM_WORLD);
  }
   // FILE *fp0; 
   //   if (my_rank == 0) {fp0=fopen("percent.map","w");printf(":MAIN:\n");}
  
   


}
