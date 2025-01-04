###############################################################################
# Makefile for CUDA version of coparam program
###############################################################################

# Directories
SRC_DIR = src
HDR_DIR = hdrs
BIN_DIR = bin

# Compiler and flags
NVCC = nvcc
NVCC_FLAGS = -O3 -I$(HDR_DIR) --device-c
NVCC_LINK_FLAGS = -O3

# Source files
CU_SOURCES = $(wildcard $(SRC_DIR)/*.cu)
CU_OBJECTS = $(CU_SOURCES:.cu=.o)

# Output program name
PROGRAM = cuda_coparam

###############################################################################
# Default Rule
###############################################################################
all: $(PROGRAM)

# Link rule
$(PROGRAM): $(CU_OBJECTS)
	$(NVCC) $(NVCC_LINK_FLAGS) $(CU_OBJECTS) -o $@

# Compilation rule for CUDA files
$(SRC_DIR)/%.o: $(SRC_DIR)/%.cu
	$(NVCC) $(NVCC_FLAGS) -c $< -o $@

###############################################################################
# Cleanup
###############################################################################
clean:
	rm -f $(SRC_DIR)/*.o $(PROGRAM)

###############################################################################
# Phony Targets
###############################################################################
.PHONY: all clean