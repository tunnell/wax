#include <stdio.h>
#include <stdlib.h>
#include <cinttypes>

#include <iostream>
#include <string>

#include <vector>
#include <cmath>

#include <boost/python/module.hpp>
#include <boost/python.hpp>
#include <boost/python/def.hpp>
#include <mongo/client/dbclient.h>
#include <mongo/client/write_concern.h>

using namespace std;
using namespace boost::python;
using namespace mongo;

void Setup(int n);
void AddSamplesFromOccurence(vector<u_int16_t>& occurence_samples,
                                int t0, int reduction);
void BuildTriggerEventRanges(vector<int> &trigger_event_ranges, int threshold, int gap);
void AssignOccurenceToTriggerEvent(vector<int> &occurence_ranges,
                                   vector<int> &trigger_event_ranges,
                                   vector<int> &occurence_mapping_to_trigger_ranges);
void get_sum(int** sum, int *n);
void shutdown();

int GetDataFromBSON(mongo::BSONObj obj, std::vector<u_int16_t>&buff, std::string &id,
                    int &module, bool &zipped, long long int &ttime, int &size);

int ProcessTimeRangeTask(long long int t0, long long int t1,
			 char* mongo_input_location,
			 char* mongo_output_location,
			 char* hostname,
			 short threshold,
			 int max_drift,
			 int padding);

bool SaveDecision(vector <mongo::BSONObj> &output_docs,
		  mongo::BSONObjBuilder* builder,
		  long long int t0, long long int t1,
		  long long int e0, long long int e1,
		  int size,
		  BSONArrayBuilder* builder_occurences_array,
		  int padding);
