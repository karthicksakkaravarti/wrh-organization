<template>
  <div>
    <v-row>
      <v-col cols="12" sm="3">
        <b>Filters</b>
        <v-col class="ma-0 pa-0">
          <DateRangePicker ref="daterangepicker" @dateselected="dateselected" />
        </v-col>
        <v-col class="ma-0 pa-0">
          <v-text-field
            v-model="Eventsearch"
            label="Id, City, Postal, Address"
            single-line
            hide-details
          ></v-text-field>
        </v-col>
        <v-col class="ma-0 pa-0">
          <v-autocomplete
            v-model="State"
            :items="StateList"
            hide-details
            label="State"
          ></v-autocomplete>
        </v-col>
        <v-col class="ma-0 pa-0">
          <v-autocomplete
            v-model="Labels"
            multiple
            :items="DisciplineList"
            small-chips
            hide-details
            label="Discipline"
          ></v-autocomplete>
        </v-col>
        <v-col class="ma-0 pa-0">
          <v-checkbox
            hide-details
            v-model="is_featured"
            label="Is Featured"
          ></v-checkbox>
        </v-col>
        <v-col class="ma-0 pa-0">
          <v-checkbox
            hide-details
            v-model="is_usac_sanctioned"
            label="Is USAC Sanctioned"
          ></v-checkbox>
        </v-col>
        <v-divider class="mt-2"></v-divider>
        <v-col class="ma-0 pa-0 mt-3">
          <div
            color="#8a8d93"
            elevation="0"
            class="d-flex justify-space-between"
          >
            <v-btn color="primary" outlined @click="ClearFilter">Clear</v-btn>

            <v-btn color="primary" @click="getEvent(null)">Search</v-btn>
          </div>
        </v-col>
      </v-col>
      <v-col cols="12" sm="9">
        <!-- <b>Results</b> -->

        <v-data-table
          :loading="EventLoader"
          dense
          :footer-props="{
            'items-per-page-options': [25],
          }"
          :headers="Eventheaders"
          :items="AcaEvent.results"
          item-key="name"
          :search="Eventsearch"
          :options.sync="pagination_events"
          :server-items-length="totalCount"
          class="elevation-1 mt-2"
        >
          <template v-slot:item.register_url="{ item }">
            <a :href="item.links.register_url">Go Ressiter</a>
          </template>
          <template v-slot:item.website_url="{ item }">
            <a :href="item.links.website_url">Go WebSite</a>
          </template>
          <template v-slot:item.labels="{ item }">
            <v-chip
              class="pl-1"
              small
              v-bind:key="i"
              v-for="i in item.labels"
              >{{ i }}</v-chip
            >
          </template>
          <template v-slot:body="{ items }">
            <tbody>
              <tr v-bind:key="i.id" v-for="i in items">
                <td>
                  <v-card elevation="0">
                    <v-card-text>
                      <v-row align="center" class="mx-0">
                        <v-col cols="12" sm="3">
                          <div class="my-3 text-subtitle-1">
                            {{
                              new Date(i.start_date).toLocaleDateString(
                                "en-us",
                                {
                                  month: "short",
                                  day: "numeric",
                                }
                              )
                            }}
                            -{{
                              new Date(i.end_date).toLocaleDateString("en-us", {
                                month: "short",
                                day: "numeric",
                              })
                            }}
                          </div>
                        </v-col>

                        <v-col cols="12" sm="9">
                          <h1>{{ i.name }}</h1>
                          <div class="ml-2">
                            {{ i.dates.address.city }},
                            {{ i.dates.address.state }},
                            {{ i.dates.address.postal }}
                          </div>
                          <v-chip
                            class="ml-1"
                            color="primary"
                            v-bind:key="i"
                            v-for="i in i.labels"
                            >{{ i }}</v-chip
                          >
                          <a
                            class="ml-2"
                            v-if="i.links.website_url"
                            :href="i.links.website_url"
                            >Website</a
                          >

                          <a
                            class="ml-2"
                            v-if="i.links.website_url"
                            :href="i.links.register_url"
                            >Register</a
                          >
                        </v-col>
                      </v-row>
                    </v-card-text>
                  </v-card>
                </td>
              </tr>
              <tr v-if="items.length == 0 && !EventLoader">
                <center>No receord found</center>
              </tr>
            </tbody>
          </template>
        </v-data-table>
      </v-col>
    </v-row>
    <!-- Filter Code -->

    <!-- Filter Code End-->
  </div>
</template>

<script>
import DateRangePicker from "@/components/DateRangePicker.vue";
import axios from "@/axios";

export default {
  components: {
    DateRangePicker,
  },
  computed: {
    totalCount() {
      var count = 25;
      // this.AcaEvent.count
      if (this.AcaEvent && this.AcaEvent.pagination) {
        return this.AcaEvent.pagination.total;
      }
      return count;
    },
  },
  mounted() {
    axios.get("/usacycling/address/list_state/").then((data) => {
      this.StateList = data.data;
    });
    axios.get("/usacycling/event/list_labels/").then((data) => {
      this.DisciplineList = data.data;
    });
  },
  data() {
    return {
      AcaEvent: [],
      DateRange: [],
      State: null,
      StateList: [],
      Labels: [],
      DisciplineList: [],

      pagination_events: {},
      Eventsearch: "",
      EventLoader: false,
      Eventheaders: [
        { text: "Results:", value: "name" },
        // { text: "Start Date", value: "start_date" },
        // { text: "State", value: "dates.address.state" },
        // { text: "Discipline", value: "labels" },
        // { text: "Register URL", value: "register_url" },
        // { text: "Website URL", value: "website_url" },
      ],
      is_featured: false,
      is_usac_sanctioned: false,
    };
  },
  watch: {
    // Eventsearch(value) {
    //   value;
    //   this.getEvent({});
    // },
    pagination_events: {
      handler(value) {
        this.getEvent(value);
      },
      deep: true,
    },
  },
  methods: {
    ClearFilter() {
      this.is_usac_sanctioned = false;
      this.is_featured = false;
      this.State = null;
      this.DateRange = [];
      this.Labels = null;
      this.Eventsearch = null;
      this.$refs.daterangepicker.date = [];
    },
    dateselected(range) {
      this.DateRange = range;
    },
    FormURL(event, endpoint) {
      var query_param = "";
      var link = endpoint;
      try {
        // Ordering Logic
        if (event && event.sortBy.length >= 1) {
          for (var [i, v] of event.sortBy.entries()) {
            if (event.sortDesc[i]) {
              query_param += "&ordering=-" + v + "&";
            } else {
              query_param += "&ordering=" + v + "&";
            }
          }
        }
        // Pagination
        if (event) {
          link += "&page=" + event.page;
        }

        // Filtering
        if (this.DateRange.length >= 1) {
          link +=
            "&range_start=" +
            this.DateRange[0] +
            "&range_end=" +
            this.DateRange[1];
        }
        if (this.State) {
          link += "&dates__address__state=" + this.State;
        }
        if (this.Labels) {
          link += "&labels=" + this.Labels;
        }
        if (this.is_featured) {
          link += "&is_featured=" + this.is_featured;
        }
        if (this.is_usac_sanctioned) {
          link += "&is_usac_sanctioned=" + this.is_usac_sanctioned;
        }
        return link + query_param;
      } catch (err) {
        return link;
      }
    },
    getEvent(event) {
      this.AcaEvent = [];
      this.EventLoader = true;
      axios.get(
        this.FormURL(event, "usacycling/event/?") +
          "&search=" +
          this.Eventsearch
      ).then((data) => {
        this.AcaEvent = data.data;
        this.EventLoader = false;
      });
    },
  },
};
</script>

<style>
</style>
