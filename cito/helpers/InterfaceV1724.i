%module inplace

%{
    #define SWIG_FILE_WITH_INIT
    #include "inplace.h"
%}

%include "numpy.i"

%init %{
    import_array();
%}

%apply (unsigned int* INPLACE_ARRAY1, int DIM1) {(unsigned int* invec, int n)}
%apply (unsigned int* INPLACE_ARRAY1, int DIM1) {(unsigned int* chan_samples, int n0)}
%apply (unsigned int* INPLACE_ARRAY1, int DIM1) {(unsigned int* chan_indecies, int n1)}
%include "inplace.h"

