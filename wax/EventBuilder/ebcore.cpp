/*Copyright 2014 Christopher Tunnell <ctunnell@nikhef.nl>

 The trigger C++ component for the 'wax' event builder software.
 
 ProcessTimeRangeTask will fetch data from MongoDB, compute a sum waveform, then
 determine the appropriate event ranges, and finally save the events back to
 MongoDB.
 
 Code is GPLv3.

 Please follow:
 http://google-styleguide.googlecode.com/svn/trunk/cppguide.xml

 And check it with cpplint.
 */
#include "./ebcore.h"

std::vector<uint32_t> sum_waveform;  // Downsampled sum waveform

vector <mongo::BSONObj> output_event_docs; // Output.
vector <mongo::BSONObj> input_occurence_docs; // Occurence docuemnt buffer

// The format of these range arrays are:
//   for event i: start_0 stop_0 start_1 stop_1 ...

// time range of every document.  units: reduced time since t0
vector <uint32_t> input_occurence_ranges;

// units: starts as the location in sum waveform, but is converted to 10 ns
// since start of run before we write back to MongoDB.
vector <int64_t> trigger_event_ranges;

// mapping from input_occurence_docs to trigger_event_ranges
vector<int> input_occurence_docs_mapping; // units: trigger event number in [0, trigger_event_ranges.size()/2)

// This is called by ProcessTimeRangeTask
void Setup(uint32_t n) {
  #if DEBUG
  cout << "Setup assuming " << n << " summed waveform bins" << endl;
  #endif

    sum_waveform.resize(n);
    std::fill(sum_waveform.begin(),
	      sum_waveform.end(),
	      0);


    output_event_docs.clear();
    input_occurence_docs.clear();
    
    input_occurence_ranges.clear();
    trigger_event_ranges.clear();
}

int32_t ProcessTimeRangeTask(int64_t t0, int64_t t1,
                               int64_t max_drift,
                               int64_t padding,
                               uint32_t threshold,
                               uint32_t reduction_factor,
                               char *hostname,
                               char *mongo_input_location,
                               char *mongo_output_location) {
    // Allocates space in the sum waveform sum_waveform and whatever ourranges
    // is
    Setup(ceil((t1 - t0) / reduction_factor));

    // Construct a mongo query for a certain time range.  The 'long long int'
    // types are required from the Mongo API.
#if DEBUG
    cout << "Setting up connection" << endl;
#endif
    ScopedDbConnection conn(hostname); 
    if(!conn.ok()) {
	cerr << "Connection not okay" << endl;
	return -1;
      }
    
#if DEBUG
    cout << "Starting query" << endl;
#endif
    mongo::Query qry = QUERY("time_min" <<
                             mongo::LT <<
                             (long long int) t1 <<
                             "time_max" <<
                             mongo::GT <<
                             (long long int) t0).sort("time_min",
                                                      1);
    auto_ptr < mongo::DBClientCursor > cursor = conn.conn().query(mongo_input_location,
								 qry);

#if DEBUG
    cout << "Query built, about to fetch data and update sum waveform" << endl;
#endif

    // Overall statistics, processed is all data read from DB, triggered is just
    // saved
    int32_t stats_processed_size = GetDataAndUpdateSumWaveform(t0, t1,
                                                                 cursor,
                                                                 reduction_factor);

    if (stats_processed_size == -1) {  // Error reported
        return -1;
    }

    // Here we build the event ranges.  This fills 'trigger_event_ranges' with
    // locations within the sum waveform corresponding to events.
    BuildTriggerEventRanges(threshold, max_drift/reduction_factor);

    input_occurence_docs_mapping.resize(input_occurence_docs.size());

    // Should be overwritten and do nothing, but keep sane defaults....
    std::fill(input_occurence_docs_mapping.begin(),
              input_occurence_docs_mapping.end(),
              -1);
    
    // Now determine for every occurence, which event it corresponds to.
    // input_occurence_docs_mapping is updated from input_occurence_ranges and
    // trigger_event_ranges
    AssignOccurenceToTriggerEvent();

    // trigger_event_ranges begins as index in sum waveform.  Convert to real
    // time required multiplying by our scaling then adding the start of our
    // search range t0 back.  This ensures that the events build in the next
    // block have the correct times.
    for (unsigned int i = 0; i < trigger_event_ranges.size(); i++) {
        trigger_event_ranges[i] *= reduction_factor;
        trigger_event_ranges[i] += t0;
    }
    
    int32_t stats_triggered_size = BuildEvent(t0, t1, padding);

    //conn.setWriteConcern(WriteConcern::unacknowledged);
    cout << "writing this many events" << output_event_docs.size() << endl;
    conn.conn().insert(mongo_output_location,  output_event_docs);
    string e = conn.conn().getLastError();
    if ( !e.empty() ) {
      cout << "insert failed: " << e << endl;
    }

    conn.done();

    return stats_processed_size;
}

// Fetch the data from MongoDB and update our calculated sum waveform
int32_t GetDataAndUpdateSumWaveform(int64_t t0, int64_t t1,
                                      auto_ptr < mongo::DBClientCursor > cursor,
                                      uint32_t reduction_factor) {
    // doc_bulk and doc_single are the MongoDB documents corresponding to a
    // 'bulk' document containing many occurences and a 'single' document
    // containing just one occurence.
    BSONObj doc_bulk, doc_single;
    std::vector<BSONElement> be;

    // Used for finding position in the sum waveform
    int64_t time_correction;

    // Fetch this per doc
    vector <uint32_t> occurence_samples;
    int module;
    int size;
    string id;
    bool zipped;
    int64_t time;

    // Collect size of all data
    u_int32_t stats_processed_size = 0;

    // Check that we could actually
    if (!cursor.get()) {
        cerr << "query failure" << endl;
        return -1;
    }

    // Iterate over all data for this query
    while (cursor->more()) {
        // Each document that the cursor returns has embedded documents within.
        doc_bulk = cursor->next();

        // Check that document actually contains occurences.
        if ( doc_bulk.hasField("bulk") == false ) {
            cerr << "No field containing bulk documents." << endl;
            return -1;
        }

        // This is an array of occurences
        be = doc_bulk.getField("bulk").Array();

        // Loop over occurences
        for (unsigned int i = 0; i < be.size(); i++) {
            doc_single = be[i].embeddedObject();

            // Clear previous occurence
            occurence_samples.clear();

            // This fills from 'doc_single' all the other arguments
            GetDataFromBSON(doc_single, occurence_samples, id, module,
                            zipped, time, size);

            // Sometimes the documents that are bundled along don't actually fall
            // within the trigger window. In this case, just skip it.
            if (time + occurence_samples.size() < t0 || time > t1) {
                continue;
            }

            time_correction = time - t0;

            // Take note of the time range corresponding to this occurence
            input_occurence_ranges.push_back(time_correction / reduction_factor);
            input_occurence_ranges.push_back((time_correction + occurence_samples.size()) / reduction_factor);

            input_occurence_docs.push_back(doc_single.copy());

            // Add samples to sum waveform
            AddSamplesFromOccurence(occurence_samples,
                                    time_correction,
                                    reduction_factor);

            stats_processed_size += size;
        }
    }
    return stats_processed_size;
}

// This takes an 'occurence', which is data seen by only one PMT
// and adds it to the sum waveform 'sum_waveform'.  This 'sum waveform'
// is stored in memory between calls to this function.
void AddSamplesFromOccurence(vector <u_int32_t> &occurence_samples,
                             int64_t t0, uint32_t reduction) {
    // Initialization
    uint32_t i = 0;
    uint32_t n = occurence_samples.size();
    uint32_t baseline = 0;
    uint32_t subindex = 0;

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
void BuildTriggerEventRanges(uint32_t threshold, int64_t gap) {
    // Temporary variable for trigger time
    int trigger_event_start_time = 0;
    int trigger_event_stop_time = 0;

    // For every bin in the sum waveform
    for (unsigned int index_of_sum_waveform_bin = 0;
            index_of_sum_waveform_bin < sum_waveform.size();
            ++index_of_sum_waveform_bin) {
        // Check if this bin is above threshold
        if (sum_waveform[index_of_sum_waveform_bin] > threshold) {
            // The start and stop time for for delta function at this bin
            trigger_event_start_time = index_of_sum_waveform_bin - gap;
            trigger_event_stop_time = index_of_sum_waveform_bin + gap + 1;

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
void AssignOccurenceToTriggerEvent() {
    // Need to multiply these by two to get location in vector
    unsigned int i_occurence = 0;  // Loop over input docs
    unsigned int i_trigger = 0;  // Keep track ourself of trigger number

    if (trigger_event_ranges.size() == 0) {
      return;
    }
    
    assert(input_occurence_ranges.size()/2 == input_occurence_docs.size());

    // Note the divide by two.  Each range is two numbers.
    for (i_occurence = 0;
         i_occurence < input_occurence_docs.size();
         i_occurence += 1) {
        // Sample is starting after our last event ends, thus try next event
        //printf("%lu %lu\n", trigger_event_ranges.size(), local_occurence_ranges.size());
        if (trigger_event_ranges[2 * i_trigger + 1] < input_occurence_ranges[2*i_occurence]) {
            // Move to next trigger event
            i_trigger += 1;

            // If we're run off array...
            if (2 * i_trigger >= trigger_event_ranges.size()) {
                // -1 means sample has no event
                input_occurence_docs_mapping[i_occurence] = -1;

                continue;
            }
        }

        // If occurence ends before next trigger event, skip
        if (input_occurence_ranges[2*i_occurence + 1] < trigger_event_ranges[2 * i_trigger]) {
            // skip event, -1 means sample has no event
            input_occurence_docs_mapping[i_occurence] = -1;
        } else {
            // Save
            input_occurence_docs_mapping[i_occurence] = i_trigger;
        }
    }
}

int32_t BuildEvent(int64_t t0, int64_t t1, int64_t padding) {
    // Create a buffer of occurences, then determine if these should be saved
    // since maybe they fall in an overlap region.
    
    mongo::BSONObjBuilder* builder =  NULL;  // TODO: when do we free this?
    BSONArrayBuilder* builder_occurences_array = NULL; // TODO: when do we free?

    int builder_mapping = 0;
    int current_size = 0;
    
    int reduced_count = 0; // Stats on how many occurences we reject
    
    u_int32_t stats_triggered_size = 0;
    
    // For every occurence we've read in, see what event it is assigned to
    for (unsigned int i = 0; i < input_occurence_docs_mapping.size(); ++i) {
#if DEBUG
      cout<<"occurence" << i << "mapping" << input_occurence_docs_mapping[i] <<endl;
#endif
      // If occurence is not assigned to event, skip
      if (input_occurence_docs_mapping[i] == -1) {
	reduced_count += 1;
	continue;
      }
      
      // If first time building BSON, or new event
      if (builder == NULL || builder_mapping != input_occurence_docs_mapping[i]) {
#if DEBUG
	cout << "First time..." << endl;
#endif

	SaveDecision(builder,
		     t0, t1,
		     trigger_event_ranges[2*builder_mapping],
		     trigger_event_ranges[2*builder_mapping + 1],
		     current_size,
		     builder_occurences_array,
		     padding);
            
            
            builder_mapping = input_occurence_docs_mapping[i];

#if DEBUG
	    cout << "Working on trigger event" << builder_mapping << endl;
#endif
            
            if (builder != NULL) {  // TODO
                delete builder;
                builder = NULL;
            }
            builder = new mongo::BSONObjBuilder();
            
            if (builder_occurences_array != NULL) {  // TODO
                delete builder_occurences_array;
                builder_occurences_array = NULL;
            }
            builder_occurences_array = new mongo::BSONArrayBuilder();
            
            builder->append("cnt", input_occurence_docs_mapping[i]);
            builder->append("compressed", false);
            
            // 'long' and 'long long' should be the same, but the Mongo API doesn't
            // seem to know about int64.  Therefore, we have to cast.
            BSONArrayBuilder bab;
            bab.append((long long int) trigger_event_ranges[2*builder_mapping]);
            bab.append((long long int) trigger_event_ranges[2*builder_mapping + 1]);
            builder->appendArray("range", bab.arr());
#if DEBUG   
            cout << "Range: [" << trigger_event_ranges[2*builder_mapping] << ", " <<
	      trigger_event_ranges[2*builder_mapping + 1] << endl;
#endif
            
            current_size = 0;
        }
        BSONObjBuilder indoc_builder;
        indoc_builder.appendElements(input_occurence_docs[i]);
        builder_occurences_array->append(indoc_builder.obj());

        // Stats
        current_size += input_occurence_docs[i].getIntField("size");
        stats_triggered_size += input_occurence_docs[i].getIntField("size");
    }
    SaveDecision(builder,
                 t0, t1,
                 trigger_event_ranges[2*builder_mapping], trigger_event_ranges[2*builder_mapping + 1],
                 current_size,
                 builder_occurences_array,
                 padding);
    
    if (builder != NULL) {  // TODO
        delete builder;
        builder = NULL;
    }
    
    if (builder_occurences_array != NULL) {  // TODO
        delete builder_occurences_array;
        builder_occurences_array = NULL;
    }
    
    return stats_triggered_size;
}

bool SaveDecision(mongo::BSONObjBuilder* builder,
                  int64_t t0, int64_t t1,
                  int64_t e0, int64_t e1,
                  int size,
                  BSONArrayBuilder* builder_occurences_array,
                  int64_t padding) {
    // Deal with situation of overlap regions... the regions between two
    // scanning ranges.  You don't want to double count events since we do save
    // some occurences from the previous scanning range to ensure we have
    // the whole drift length.
    //
    // Padding should be done in 'real units'.
    
    if (builder != NULL && builder_occurences_array != NULL) {
        builder->append("size", size);
        builder->appendArray("docs", builder_occurences_array->arr());

        // Check for mega event: event spanning many search ranges (i.e.,
        // chunks).  This means that the padding/overlap between chunks is too
        // small.  Or something crazy happened in the detector.

        if (e1 > t1 && e0 < t1 - padding) {
            cerr << "FATAL ERROR IN COMPILED COMPONENT:" << endl;
            cerr << "Event spans two search blocks (mega-event?)" << endl;
            cerr << "e1 " << e1 << " t1 " << t1 << " " << (e1 > t1) << endl;
            cerr << "e0 " << e0 << " t1 - padding" << t1 - padding << " ";
            cerr << (e0 < t1 - padding) << endl;
            exit(-1);
        }

        // Save event
        if (e0 >= t0 + padding && e1 <= t1) {
            output_event_docs.push_back(builder->obj());
            // cout<<"SUCCESS!!!";
        } else {
            cout << "fail:" << endl;
            cout << "\te0:" << e0 << endl;
            cout << "\tt0:" << t0 << endl;
            cout << "\tpadding:" << padding << endl;
            cout << "\te1:" << e1 << endl;
            cout << "\tt1:" << t1 << endl;
        }
    }
    return true;
}

int GetDataFromBSON(mongo::BSONObj obj, vector <uint32_t> &buff, string & id,
                    int &module, bool & zipped, int64_t &ttime, int &size) {
    module = obj.getIntField("module");
    ttime = obj.getField("time").numberLong();

    // 'size' is in bytes
    u_int32_t *raw = (u_int32_t*)(obj.getField("data").binData(size));

    // 'raw' contains two 14-bit numbers in every element
    for (int x = 0; x < (size / 4); x++) {
        buff.push_back(raw[x] & 0x3FFF);
        buff.push_back((raw[x] >> 16) & 0x3FFF);
    }
    return 0;
}


BOOST_PYTHON_MODULE(ebcore) {
    def("process_time_range_task", ProcessTimeRangeTask);
}
