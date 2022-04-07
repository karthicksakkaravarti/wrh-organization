<template>
  <div>
    <v-row>
      <v-col cols="12" sm="3">
        <b>Filters</b>

        <v-col class="ma-0 pa-0">
          <v-text-field
            v-model="Search"
            label="Rider Name / License / State"
            single-line
            hide-details
          ></v-text-field>
          <v-col class="ma-0 pa-0">
            <v-autocomplete
              v-model="State"
              :items="StateList"
              hide-details
              label="State"
            ></v-autocomplete>
          </v-col>
        </v-col>

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
          :loading="RiderLoader"
          dense
          :footer-props="{
            'items-per-page-options': [25],
          }"
          :headers="Eventheaders"
          :items="RiderList.results"
          item-key="name"
          :search="Search"
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
        </v-data-table>
      </v-col>
    </v-row>
    <!-- Filter Code -->

    <!-- Filter Code End-->
  </div>
</template>

<script>
import axios from "@/axios";
export default {
  computed: {
    totalCount() {
      var count = 25;
      if (this.RiderList && this.RiderList.pagination) {
        return this.RiderList.pagination.total;
      }
      return count;
    },
  },

  data() {
    return {
      RiderList: [],
      State: null,
      StateList: [],
      Labels: [],
      DisciplineList: [],

      pagination_events: {},
      Search: "",
      RiderLoader: false,
      Eventheaders: [
        { text: "State", value: "state" },
        { text: "License", value: "license" },
        { text: "Lic Expiration", value: "expdatemtn" },
        { text: "First Name", value: "firstname" },
        { text: "Last Name", value: "lastname" },
      ],
      is_featured: false,
      is_usac_sanctioned: false,
    };
  },
  watch: {
    // Search(value) {
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
  mounted() {
    axios.get("usacycling/rider/list_state/").then((data) => {
      this.StateList = data.data;
    });
  },
  methods: {
    ClearFilter() {
      this.State = null;
      this.Labels = null;
      this.Search = null;
    },
    dateselected(range) {
      console.log(range);
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
        if (this.State) {
          link += "&state=" + this.State;
        }

        return link + query_param;
      } catch (err) {
        console.log(err);
        return link;
      }
    },
    getEvent(event) {
      this.RiderList = [];
      this.RiderLoader = true;
      axios
        .get(
          this.FormURL(event, "usacycling/rider/?") +
            "&search=" +
            this.Search
        )
        .then((data) => {
          this.RiderList = data.data;
          this.RiderLoader = false;
        });
    },
  },
};
</script>

<style>
</style>
