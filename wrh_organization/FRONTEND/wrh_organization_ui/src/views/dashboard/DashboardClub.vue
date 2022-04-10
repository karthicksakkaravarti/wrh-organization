<template>
  <div>
    <v-row>
      <v-col cols="12" sm="3">
        <b>Filters</b>

        <v-col class="ma-0 pa-0">
          <v-text-field
            v-model="search"
            label="Club"
            single-line
            hide-details
          ></v-text-field>
          <v-col class="ma-0 pa-0">
            <v-autocomplete
              v-model="State"
              :items="StateList"
              hide-details
              label="Type"
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
          :loading="ClubLoader"
          dense
          :footer-props="{
            'items-per-page-options': [25],
          }"
          :headers="Eventheaders"
          :items="Club.results"
          item-key="name"
          :search="search"
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
                        <v-col cols="12" sm="9">
                          <h1>{{ i.club_name }}</h1>
                          <div class="ml-2">
                            {{ i.club_id }}
                          </div>
                          <v-chip class="ml-1" color="primary"
                            >Teams :{{ i.club_teams.length }}</v-chip
                          >
                          <v-chip class="ml-1" color="primary">{{
                            i.club_aff_type.aff_type_description
                          }}</v-chip>
                          <!-- <a class="ml-2" v-if="i.links.website_url" :href="i.links.website_url">Website</a>

                          <a class="ml-2" v-if="i.links.website_url"  :href="i.links.register_url">Register</a> -->
                        </v-col>
                      </v-row>
                    </v-card-text>
                  </v-card>
                </td>
              </tr>
              <tr v-if="items.length == 0 && !ClubLoader">
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
import axios from "@/axios";
export default {
  computed: {
    totalCount() {
      var count = 25;
      // this.Club.count
      if (this.Club && this.Club.pagination) {
        return this.Club.pagination.total;
      }
      return count;
    },
  },

  data() {
    return {
      Club: [],
      DateRange: [],
      State: null,
      StateList: [],
      Labels: [],
      DisciplineList: [],

      pagination_events: {},
      search: "",
      ClubLoader: false,
      Eventheaders: [{ text: "Results:", value: "name" }],
      is_featured: false,
      is_usac_sanctioned: false,
    };
  },
  mounted() {
    axios.get("usacycling/club/list_type/").then((data) => {
      this.StateList = data.data;
    });
  },
  watch: {
    pagination_events: {
      handler(value) {
        this.getEvent(value);
      },
      deep: true,
    },
  },
  methods: {
    ClearFilter() {
      this.State = null;
      this.search = null;
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
          link += "&club_aff_type__aff_type_description=" + this.State;
        }

        return link + query_param;
      } catch (err) {
        console.log(err);
        return link;
      }
    },
    getEvent(event) {
      this.Club = [];
      this.ClubLoader = true;
      axios
        .get(
          this.FormURL(event, "usacycling/club/?") +
            "&search=" +
            (this.search || "")
        )
        .then((data) => {
          this.Club = data.data;
          this.ClubLoader = false;
        });
    },
  },
};
</script>

<style>
</style>
