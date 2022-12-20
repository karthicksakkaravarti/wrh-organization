
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
import {appendScriptToHeader, randomId} from "@/composables/utils";


export default {
  components: {
  },
  setup() {
    const twitterId = "twitter-wjs-" + randomId();
    onMounted(() => {
      appendScriptToHeader(document, "https://platform.twitter.com/widgets.js", twitterId)
    });

    onBeforeUnmount(() => {
      document.getElementById(twitterId).remove();
    });

    return {
    }
  },
}
</script>

