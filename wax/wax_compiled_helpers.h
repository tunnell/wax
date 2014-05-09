void setup(int n);
void add_samples(int* samples, int n,
                 int t0, int reduction);
void build_events(int **ranges, int *n, int threshold, int gap);
void overlaps(int **samples_indices, int *n,
              int *samples_ranges, int n2);
void get_sum(int** sum, int *n);
void shutdown();
