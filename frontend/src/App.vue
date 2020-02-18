<template>
  <v-app>
    <SbcLayout>
      <HelloWorld></HelloWorld>
    </SbcLayout>
  </v-app>
</template>

<script lang="ts">
import Vue from "vue";
import "@bcgov/bc-sans/css/BCSans.css";
import SbcLayout from "sbc-common-components/src/components/SbcLayout.vue";
import HelloWorld from "@/components/HelloWorld.vue";

export default Vue.extend({
  components: {
    SbcLayout,
    HelloWorld
  },

  data: () => ({
    //
  })
});
</script>

<style lang="scss"></style>
