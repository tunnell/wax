#include <stdio.h>
#include <stdlib.h>

#include <iostream>
#include <string>

#include <vector>
#include <cmath>
#include <algorithm>    // std::fill

#include <assert.h>

#include <boost/python/module.hpp>
#include <boost/python.hpp>
#include <boost/python/def.hpp>
#include <mongo/client/dbclient.h>

using namespace std;
using namespace boost::python;
using namespace mongo;

void Setup(uint32_t n);

int32_t ProcessTimeRangeTask(int64_t t0, int64_t t1,
                               int64_t max_drift,
                               int64_t padding,
                               uint32_t threshold,
                               uint32_t reduction_factor,
                               char *hostname,
                               char *mongo_input_location,
                               char *mongo_output_location);

int32_t GetDataAndUpdateSumWaveform(int64_t t0, int64_t t1,
                                      auto_ptr < mongo::DBClientCursor > cursor,
                                      int reduction_factor);

void AddSamplesFromOccurence(std::vector<uint32_t>& occurence_samples,
                             int64_t t0, uint32_t reduction);
void BuildTriggerEventRanges(uint32_t threshold, int64_t gap);
void AssignOccurenceToTriggerEvent();

int32_t BuildEvent(int64_t t0, int64_t t1, int64_t padding);

bool SaveDecision(mongo::BSONObjBuilder* builder,
                  int64_t t0, int64_t t1,
                  int64_t e0, int64_t e1,
                  int size,
                  mongo::BSONArrayBuilder* builder_occurences_array,
                  int padding);

int GetDataFromBSON(mongo::BSONObj obj, std::vector<uint32_t>&buff,
                    std::string &id, int &module, bool &zipped, int64_t &ttime,
                    int &size);





