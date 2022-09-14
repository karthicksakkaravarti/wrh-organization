
<template>
  <v-card>
    <a class="twitter-timeline text-decoration-none pl-2" data-height="425" data-chrome="transparent noborders"
       :data-theme="$vuetify.theme.isDark? 'dark': null" href="https://twitter.com/BicycleColo">
      <v-progress-circular indeterminate color="primary" size="20" width="3"></v-progress-circular>
      Waiting for BicycleColo twitter ...
    </a>
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

