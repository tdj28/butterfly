ifneq (,)
    This makefile requires GNU Make.
endif

SRC_DIR = src
HDR_DIR = hdrs
BIN_DRI = bin
MPI_DIR = /data/project/mpich-install/include
CFLAGS = -O2 -DDEBUG=1 -I./$(HDR_DIR) -I$(MPI_DIR) 
CC =mpicc
LDFLAGS = -lm

PROGRAM = coparam
C_FILES := $(wildcard $(SRC_DIR)/*.c)
OBJS := $(patsubst %.c, %.o, $(C_FILES))

all: $(PROGRAM)

$(PROGRAM): .depend $(OBJS)
	$(CC) $(CFLAGS) $(OBJS) $(LDFLAGS) -o $(PROGRAM)

depend: .depend

.depend: cmd = gcc -MM -MF depend $(var); cat depend >> .depend;
.depend:
	@echo "Generating dependencies..."
	@$(foreach var, $(C_FILES), $(cmd))
	@rm -f depend

-include .depend

    # These are the pattern matching rules. In addition to the automatic
    # variables used here, the variable $* that matches whatever % stands for
    # can be useful in special cases.
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

%: %.c
	$(CC) $(CFLAGS) -o $@ $<
clean:
	rm -f .depend $(SRC_DIR)/*.o $(PROGRAM)

.PHONY: clean depend

#all: $(SRC_DIR)/derivs.c $(SRC_DIR)/rk4.c $(SRC_DIR)/poincare.c $(SRC_DIR)/advance.c $(SRC_DIR)/advancem.c $(SRC_DIR)/checkin.c $(SRC_DIR)/startup.c $(SRC_DIR)/main.c 
#	$(CC) $(CFLAGS) -o $(BIN_DIR)/a.out $(SRC_DIR)/derivs.c $(SRC_DIR)/rk4.c $(SRC_DIR)/poincare.c $(SRC_DIR)/advance.c $(SRC_DIR)/advancem.c $(SRC_DIR)/checkin.c $(SRC_DIR)/startup.c $(SRC_DIR)/main.c -lm	

#clean:
#	rm -rf *o a.out














#all:  derivs.c rk4.c poincare.c advance.c  advancem.c  checkin.c  startup.c main.c
#	${CC} ${CFLAGS} derivs.c rk4.c poincare.c advance.c  advancem.c  checkin.c startup.c main.c -o a.out

#all:  rest.o main.o 
#	${CC} ${CFLAGS} main.o rest.o -o a.out 


#main.o: main.c 
#	${CC} ${CFLAGS} -c main.c

#globals.o: globals.c
#	${CC} ${CFLAGS} -c globals.c

#rest.o: advance.c  advancem.c  checkin.c  derivs.c  poincare.c  rk4.c  startup.c
#	${CC} ${CFLAGS} advance.c  advancem.c  checkin.c  derivs.c  poincare.c  rk4.c  startup.c -o rest.o




#OBJECTS=$(SOURCES:.cpp=.o)
