<template>
  <v-btn color="primary">{{ title }}</v-btn>
</template>

<script>
export default {
  props: {
    title: {
      default: null,
      type: String
    }
  }
};
</script>

<style>
</style>