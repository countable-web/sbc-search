<template>
  <v-app>
    <SbcHeader></SbcHeader>

    <v-content>
      <HelloWorld />
    </v-content>
  </v-app>
</template>

<script lang="ts">
import Vue from "vue";
import SbcHeader from "sbc-common-components/src/components/SbcHeader.vue";

import HelloWorld from "./components/HelloWorld.vue";

export default Vue.extend({
  name: "App",

  components: {
    HelloWorld,
    SbcHeader
  },

  data: () => ({
    //
  })
});
</script>
