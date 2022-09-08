
<template>
  <v-card>
    <a class="twitter-timeline" data-height="425" data-chrome="transparent noborders" :data-theme="$vuetify.theme.isDark? 'dark': null" href="https://twitter.com/BicycleColo?ref_src=twsrc%5Etfw">Tweets by BicycleColo</a>
  </v-card>

</template>


<script>
import * as TwitterWidget from '@/plugins/twitter-widgets';

export default {
  components: {
  },
  setup() {

    return {
    }
  },
}
</script>

