%module CaenBlockParsing

%{
    #define SWIG_FILE_WITH_INIT
    #include "CaenBlockParsing.h"
%}

%include "numpy.i"

%init %{
    import_array();
%}

%apply (unsigned int* INPLACE_ARRAY1, int DIM1) {(unsigned int* invec, int n)}
%apply (int* INPLACE_ARRAY1, int DIM1) {(short* chan_samples, int n0)}
%apply (unsigned int* INPLACE_ARRAY1, int DIM1) {(unsigned int* chan_indecies, int n1)}
%apply (int* ARGOUT_ARRAY1, int DIM1) {(short *sum_waveform_out, int n)}

%include "CaenBlockParsing.h"

