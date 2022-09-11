
<template>
  <v-card>
    <a class="twitter-timeline" data-height="425" data-chrome="transparent noborders" :data-theme="$vuetify.theme.isDark? 'dark': null" href="https://twitter.com/BicycleColo?ref_src=twsrc%5Etfw">Tweets by BicycleColo</a>
  </v-card>

</template>


<script>
import {onMounted, onBeforeUnmount} from "@vue/composition-api";
import {randomId} from "@/composables/utils";


export default {
  components: {
  },
  setup() {
    const twitterId = "twitter-wjs-" + randomId();
    const loadTwitter = function (d, s, id) {
      if (d.getElementById(id)) {
        d.getElementById(id).remove();
      }
      var t = {};
      var js, fjs = d.getElementsByTagName(s)[0];
      js = d.createElement(s);
      js.id = id;
      js.src = "https://platform.twitter.com/widgets.js";
      fjs.parentNode.insertBefore(js, fjs);

      t._e = [];
      t.ready = function (f) {
        t._e.push(f);
      };

      return t;
    };

    onMounted(() => {
      loadTwitter(document, "script", twitterId);
    });

    onBeforeUnmount(() => {
      document.getElementById(twitterId).remove();
    });

    return {
    }
  },
}
</script>

