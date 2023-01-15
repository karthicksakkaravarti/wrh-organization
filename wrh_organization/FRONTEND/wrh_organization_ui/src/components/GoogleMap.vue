<template>
  <div>
    <v-autocomplete
      v-if="!isEditMode"
      outlined
      dense
      v-model="address"
      :items="items"
      clerable
      name="address"
      :search-input.sync="search"
      label="Address"
      placeholder="Address"
      class="pa-3"
      autocomplete="off"
      :filter="(d) => d"
      color="secondary"
      item-color="secondary"
      return-object
      @change="selected_address"
    ></v-autocomplete>

    <GmapMap
      :center="{
        lat: crd.lat,
        lng: crd.lng,
      }"
      :zoom="7"
      :style="sty"
    >
      <GmapMarker
        :position="{
          lat: crd.lat,
          lng: crd.lng,
        }"
        :draggable="true"
        @drag="updateCoordinates"
      ></GmapMarker>
    </GmapMap>
  </div>
</template>

<script>
import geolocation from "vue-browser-geolocation";

export default {
  props: {
    more_data: { default: null },
    isEditMode: { default: false },
    sty: { default: "width: 640px; height: 360px" },
  },
  data() {
    return {
      crd: { lat: 0, lng: 0 },
      eventCoordinate: { lat: 0, lng: 0 },
      items: [],
      search: null,
      address: null,
    };
  },
  watch: {
    search(value) {
      //Optional: here you can add some delay
      this.googleSearch(value);
    },
    more_data(value) {
      console.log(value);
      if (value && value.lat && value.lng) {
        this.crd.lat = value.lat;
        this.crd.lng = value.lng;
      }
    },
  },
  methods: {
    getCurrentLocation() {
      if (!this.isEditMode) {
        geolocation
          .getLocation({})
          .then((coordinates) => {
            this.crd = coordinates;
          })
        
      }
    },
    updateCoordinates(location) {
      if (location && location.latLng) {
        try {
          this.eventCoordinate.lat = location.latLng.lat();
          this.eventCoordinate.lng = location.latLng.lng();
        } catch (err) {
          err;
        }
      } else {
        try {
          this.eventCoordinate.lat = location.lat;
          this.eventCoordinate.lng = location.lng;
        } catch (err) {
          err;
        }
      }

      this.$emit("coordinates", this.eventCoordinate);
    },
    selected_address() {
      this.crd.lat = this.address.value.geometry.location.lat;
      this.crd.lng = this.address.value.geometry.location.lng;
      this.updateCoordinates(this.address.value.geometry.location);
    },
    googleSearch(value) {
      if (value) {
        let url =
          "https://maps.googleapis.com/maps/api/geocode/json?key="+process.env.VUE_APP_GMAP_TOKEN+"&address=";
        fetch(url + value)
          .then((response) => {
            return response.json();
          })
          .then((jsonResult) => {
            this.items = jsonResult.results.map((item) => {
              //You can explore and use other information inside "item" like latitude, longitude, country, City, zipCode
              return {
                text: item.formatted_address,
                value: item,
              };
            });
          })
          .catch((err) => {
            //handle errors
            console.log(err);
          });
      }
    },
  },
  mounted() {
    this.getCurrentLocation();
    this.updateCoordinates();
    if (this.more_data && this.more_data.lat && this.more_data.lng) {
        this.crd.lat = this.more_data.lat;
        this.crd.lng = this.more_data.lng;
      }
  },
};
</script>

<style>
</style>