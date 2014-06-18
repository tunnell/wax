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

void Setup(uint32_t n);

u_int32_t ProcessTimeRangeTask(int64_t t0, int64_t t1,
                               int64_t max_drift,
                               int64_t padding,
                               uint32_t threshold,
                               char *hostname,
                               char *mongo_input_location,
                               char *mongo_output_location);

void Shutdown();

void AddSamplesFromOccurence(vector<uint32_t>& occurence_samples,
                             int t0, int reduction);
void BuildTriggerEventRanges(vector<int64_t> &trigger_event_ranges, uint32_t threshold, int64_t gap);
void AssignOccurenceToTriggerEvent(vector<uint32_t> &occurence_ranges,
                                   vector<int64_t> &trigger_event_ranges,
                                   vector<int> &occurence_mapping_to_trigger_ranges);
void GetSum(int** sum, int *n);


int GetDataFromBSON(mongo::BSONObj obj, std::vector<uint32_t>&buff, std::string &id,
                    int &module, bool &zipped, int64_t &ttime, int &size);



bool SaveDecision(vector <mongo::BSONObj> &output_docs,
                  mongo::BSONObjBuilder* builder,
                  int64_t t0, int64_t t1,
                  int64_t e0, int64_t e1,
                  int size,
                  BSONArrayBuilder* builder_occurences_array,
                  int padding);


