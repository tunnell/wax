/*Copyright 2014 Christopher Tunnell <ctunnell@nikhef.nl>

 Code is GPLv3.

 Please follow:
 http://google-styleguide.googlecode.com/svn/trunk/cppguide.xml

 And check it with cpplint.
 */
#include "wax_compiled_helpers.h"

int *sum_waveform = NULL;

// length of sum_waveform
int sum_waveform_n = 0;

int *ourranges = NULL;
int ourrangeindex = 0;


int i = 0;
int subindex = 0;

int baseline = 0;

// This takes an 'occurence', which is data seen by only one PMT
// and adds it to the sum waveform 'sum_waveform'.  This 'sum waveform'
// is stored in memory between calls to this function.
void AddSamplesFromOccurence(vector < u_int16_t > &occurence_samples,
                                int t0, int reduction) {
    int n = occurence_samples.size();

    // A PMT pulse is normally a dip from a baseline, so we want to invert this
    // signal such that we can find a maximum.  These are 14-bit ADCs, so we
    // add 2^14 = 16384 to have positive pulses.
    for (i = 0; i < n; ++i) {
        occurence_samples[i] = -1 * occurence_samples[i] + 16384;
    }

    // We estimate the baseline by assuming the first three samples do not
    // contain signal.  This should be true since the digitizers should data
    // before and after a pulse that causes a self trigger on the board.  The
    // baseline is thus the average of these first three samples.
    baseline = 0;
    baseline += occurence_samples[0];
    baseline += occurence_samples[1];
    baseline += occurence_samples[2];
    baseline /= 3;

    // Add all the samples from this occurence to the sum waveform.
    for (i = 0; i < n; ++i) {
        // Compute a position (including our reduction factor).
        subindex = (t0 + i) / reduction;

        // Then add to sum waveform, but removing baseline.
        sum_waveform[subindex] += occurence_samples[i] - baseline;
    }
}

// For every contigous time block of samples above threshold [t0, t1], save a
// range of [t0 - gap, t1 + gap].  Each one of this contigous time blocks is
// a 'trigger event'.
void BuildTriggerEventRanges(vector<int> &trigger_event_ranges,
                                int threshold, int gap) {
    // Temporary variable for trigger time
    int trigger_event_start_time = 0;
    int trigger_event_stop_time = 0;

    // For every bin in the sum waveform
    for (int index_of_sum_waveform_bin = 0;
         index_of_sum_waveform_bin < sum_waveform_n;
         ++index_of_sum_waveform_bin) {
        // Check if this bin is above threshold
        if (sum_waveform[index_of_sum_waveform_bin] > threshold) {
            // The start and stop time for for delta function at this bin
            trigger_event_start_time = index_of_sum_waveform_bin - gap;
            trigger_event_stop_time = index_of_sum_waveform_bin + gap;

            // But these need to be compared to what has already been seen. If
            // the start time of this bin is within the last seen range, then
            // merge this bin's range with the previous seen range.  Otherwise,
            // create a new range.
            if (trigger_event_ranges.size() > 0 && trigger_event_start_time < trigger_event_ranges.back()) {
                trigger_event_ranges.pop_back();
                trigger_event_ranges.push_back(trigger_event_stop_time);
            } else {
                trigger_event_ranges.push_back(trigger_event_start_time);
                trigger_event_ranges.push_back(trigger_event_stop_time);
            }
        }
    }
}


// For every occurence document, determine which trigger event it corresponds to.
void AssignOccurenceToTriggerEvent(vector<int> &occurence_ranges,
                                   vector<int> &trigger_event_ranges,
                                   vector<int> &occurence_mapping_to_trigger_ranges) {
    // Need to multiply these by two to get location in vector
    int i_occurence = 0;
    int i_trigger = 0;

    // Note the divide by two.  Each range is two numbers.
    for (i_occurence = 0;
         i_occurence < (occurence_ranges.size()/2);
         i_occurence += 1) {
        // Sample is starting after our last event ends, thus try next event
        if (trigger_event_ranges[2 * i_trigger + 1] < occurence_ranges[2*i_occurence]) {
            // Move to next trigger event
            i_trigger += 1;

            // If we're run off array...
            if (2 * i_trigger >= trigger_event_ranges.size()) {
                // -1 means sample has no event
                occurence_mapping_to_trigger_ranges[i_occurence] = -1;

                continue;
            }
        }

        // If occurence ends before next trigger event, skip
        if (occurence_ranges[2*i_occurence + 1] < trigger_event_ranges[2 * i_trigger]) {
            // skip event, -1 means sample has no event
            occurence_mapping_to_trigger_ranges[i_occurence] = -1;
        } else {
            // Save
            occurence_mapping_to_trigger_ranges[i_occurence] = i_trigger;
        }
    }
}

void shutdown() {
    if (sum_waveform != NULL)
        free(sum_waveform);
    sum_waveform = NULL;
    if (ourranges != NULL)
        free(ourranges);
    ourranges = NULL;
}

void Setup(int n) {
    if (sum_waveform_n != 0 && sum_waveform_n != n) {
        printf("wax_compiled_helpers already initialized; will try to reinitialize...\n");
        shutdown();
    }
    if (sum_waveform == NULL) {
        sum_waveform = (int *)malloc(sizeof(int) * n);
    }
    if (ourranges == NULL) {
        ourranges = (int *)malloc(sizeof(int) * n * 2);
    }
    memset(sum_waveform, 0, sizeof(int) * n);
    memset(ourranges, 0, sizeof(int) * n * 2);
    sum_waveform_n = n;
}

bool SaveDecision(vector <mongo::BSONObj> &output_docs,
                mongo::BSONObjBuilder* builder,
                 long long int t0, long long int t1,
                 long long int e0, long long int e1,
                 int size,
                 BSONArrayBuilder* builder_occurences_array,
                 int padding){
  if(builder != NULL) {
    builder->append("size", size);
    builder->appendArray("docs", builder_occurences_array->arr());

    // Check for mega event: event spanning many search ranges (i.e., chunks).
    // This means that the padding/overlap between chunks is too small.  Or
    // something crazy happened in the detector.
    if (e1 > t1 && e0 < t1 - padding) {
      cerr << "FATAL ERROR IN COMPILED COMPONENT:" << endl;
      cerr << "Event spans two search blocks (mega-event?)" << endl;
      return false;
    }

    // Save event
    if (e0 > t0 + padding && e1 < t1) {
      output_docs.push_back(builder->obj());
    }
  }
  return true;
}

int ProcessTimeRangeTask(long long int t0, long long int t1,
                           char *mongo_input_location,
                           char *mongo_output_location,
                           char *hostname,
                           short threshold,
                           int max_drift,
                           int padding) {
    mongo::DBClientConnection conn;
    conn.connect(hostname);

    // Overall statistics
    int     processed_size = 0;

    // Fetch this per doc
    vector < u_int16_t > occurence_samples;
    int     module, size;
    string      id;
    bool        zipped;
    int64_t   time;

    int64_t   time_correction;
    int     reduction_factor = 100;
    int     n = ceil((t1 - t0) / reduction_factor);

    // Setup the sum waveform
    Setup(n);

    vector <mongo::BSONObj> input_docs;

    // Store the time range of every document.   This is not moved to a seperate
    // function that operated on 'docs' because it requires parsing the data
    // payload to determine the end time.  The format of the array is:
    //
    //   for event i: start_0 stop_0 start_1 stop_1 ...
    vector <int> occurence_ranges;

    // Same, but for trigger-event ranges
    vector <int> trigger_event_ranges;

    mongo::BSONObj p;
    auto_ptr < mongo::DBClientCursor > cursor = conn.query(mongo_input_location,
                                                            QUERY("time" << mongo::GT << t0 << "time" << mongo::LT << t1).sort("time", 1));
    while (cursor->more()) {
        p = cursor->next();
        occurence_samples.clear();
        GetDataFromBSON(p, occurence_samples, id, module, zipped, time, size);

        time_correction = time - t0;

        // Take note of the time range corresponding to this occurence
        occurence_ranges.push_back(time_correction / reduction_factor);
        occurence_ranges.push_back((time_correction + occurence_samples.size()) / reduction_factor);

        input_docs.push_back(p.copy());

        // Add samples to sum waveform
        AddSamplesFromOccurence(occurence_samples,
                                   time_correction,
                                   reduction_factor);

        processed_size += size;
    }

    // Here we build the event ranges
    BuildTriggerEventRanges(trigger_event_ranges, threshold,
                            max_drift/reduction_factor);

    vector <int> occurence_mapping_to_trigger_ranges(occurence_ranges.size()/2);

    // Now determine for every occurence, which event it corresponds to.  The
    // first two ranges vectors are inputs, the mapping is the output.
    AssignOccurenceToTriggerEvent(occurence_ranges,
                                  trigger_event_ranges,
                                  occurence_mapping_to_trigger_ranges);

    vector <mongo::BSONObj> output_docs;

    mongo::BSONObjBuilder* builder =  NULL;
    BSONArrayBuilder* builder_occurences_array = NULL;
    int builder_mapping = 0;
    int current_size = 0;

    int reduced_count = 0;
    for (int i = 0; i < occurence_mapping_to_trigger_ranges.size(); ++i) {
        if (occurence_mapping_to_trigger_ranges[i] == -1) {
            reduced_count += 1;
            continue;
        }

        // If first time building BSON, or new event
        if (builder == NULL || builder_mapping != occurence_mapping_to_trigger_ranges[i]) {
            SaveDecision(output_docs,
                         builder,
                         t0, t1,
                         trigger_event_ranges[2*builder_mapping], trigger_event_ranges[2*builder_mapping + 1],
                         current_size,
                         builder_occurences_array,
                         padding);


            builder_mapping = occurence_mapping_to_trigger_ranges[i];

            builder = new mongo::BSONObjBuilder();
            builder_occurences_array = new mongo::BSONArrayBuilder();
            builder->append("cnt", occurence_mapping_to_trigger_ranges[i]);
            builder->append("compressed", false);

            BSONArrayBuilder bab;
            bab.append(trigger_event_ranges[2*builder_mapping]);
            bab.append(trigger_event_ranges[2*builder_mapping + 1]);
            builder->appendArray("range", bab.arr());

            current_size = 0;
        }
        BSONObjBuilder indoc_builder;
        indoc_builder.appendElements(input_docs[i]);
        builder_occurences_array->append(indoc_builder.obj());
        current_size += input_docs[i].getIntField("size");
    }
    SaveDecision(output_docs,
                 builder,
                 t0, t1,
                 trigger_event_ranges[2*builder_mapping], trigger_event_ranges[2*builder_mapping + 1],
                 current_size,
                 builder_occurences_array,
                 padding);

    conn.setWriteConcern(WriteConcern::unacknowledged);
    conn.insert("outputy.test", output_docs);

    return processed_size;
}

int GetDataFromBSON(mongo::BSONObj obj, vector < u_int16_t > &buff, string & id,
                int &module, bool & zipped, int64_t &ttime, int &size) {
    module = obj.getIntField("module");
    ttime = obj.getField("time").numberLong();

    // 'size' is in bytes
    u_int32_t *raw = (u_int32_t*)(obj.getField("data").binData(size));

    for (unsigned int x = 0; x < (size / 4); x++) {
        buff.push_back(raw[x] & 0x3FFF);
        buff.push_back((raw[x] >> 16) & 0x3FFF);
    }
    return 0;
}

BOOST_PYTHON_MODULE(waxcore) {
    def("process_time_range_task", ProcessTimeRangeTask);
}
