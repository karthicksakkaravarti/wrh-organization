<template>
      <v-menu
        ref="menu"
        v-model="menu"
        :close-on-content-click="false"
        :return-value.sync="date"
        transition="scale-transition"
        offset-y
        min-width="auto"
      >
        <template v-slot:activator="{ on, attrs }">
          <v-text-field
          hide-details
            v-model="date"
            label="Date Range"
            readonly
            v-bind="attrs"
            v-on="on"
          ></v-text-field>
        </template>
        <v-date-picker range v-model="date" no-title scrollable>
          <v-spacer></v-spacer>
          <v-btn text color="primary" @click="menu = false"> Cancel </v-btn>
          <v-btn text color="primary" @click="ok(date)">
            OK
          </v-btn>
        </v-date-picker>
      </v-menu>

</template>


<script>
export default {
    methods:{
        ok(date){
        
            this.$refs.menu.save(date)
            this.$emit('dateselected', date)
        }
    },
  data: () => ({
    date: [],
    menu: false,
    modal: false,
    menu2: false,
  }),
};
</script>