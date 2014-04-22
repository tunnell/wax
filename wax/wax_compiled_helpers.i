%module wax_compiled_helpers

%{
    #define SWIG_FILE_WITH_INIT
    #include "wax_compiled_helpers.h"
%}

%include "numpy.i"

%init %{
    import_array();
%}

%apply (int* IN_ARRAY1, int DIM1) {(int* samples, int n)}
%apply (int** ARGOUTVIEW_ARRAY1, int *DIM1) {(int** sum, int *n)}
%apply (int** ARGOUTVIEW_ARRAY1, int *DIM1) {(int** ranges, int *n)}

%apply (int* IN_ARRAY1, int DIM1) {(int *samples_ranges, int n2)}
%apply (int** ARGOUTVIEW_ARRAY1, int *DIM1) {(int **samples_indices, int *n)}

%include "wax_compiled_helpers.h"

