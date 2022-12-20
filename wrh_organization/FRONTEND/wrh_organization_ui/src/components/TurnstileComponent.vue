<script>
import {defineComponent, onMounted, ref} from '@vue/composition-api'

export default defineComponent({
  name: "TurnstileComponent",
  props: {
    sitekey: {
      type: String,
      required: true
    }
  },
  emits: {
    verify: (response) => {
      return (response !== null && response !== "");
    },
    expire: null,
    fail: null,
    timeout: null,
  },
  setup(props, context) {
    const turnstileBoxRef = ref(null);
    window.onloadTurnstileCallback = () => {
      renderTurnstile();
    };

    onMounted(() => {
      if (!window.turnstile) {
        const script = document.createElement('script');
        script.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js?onload=onloadTurnstileCallback';
        script.async = true;
        script.defer = true;
        document.head.appendChild(script);
      } else {
        renderTurnstile();
      }
    });

    const renderTurnstile = () => {
        window.turnstile?.render(`#${turnstileBoxRef.value.id}`, {
          sitekey: props.sitekey,
          callback: (response) => context.emit('verify', response),
          'expired-callback': () => context.emit('expire'),
          'error-callback': () => context.emit('fail'),
          'timeout-callback': () => context.emit('timeout'),
        })
    };

    const reset = () => {
      window.turnstile?.reset(`#${turnstileBoxRef.value.id}`);
    };
    return {
      reset,
      turnstileBoxRef
    }
  }

})
</script>

<template>
  <div ref="turnstileBoxRef" id="turnstile-box"></div>
</template>

<style scoped>

</style>
