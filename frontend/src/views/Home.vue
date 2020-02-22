<template>
  <div class="home">
    <h1>Welcome to Director Search</h1>
    <h4 class="mt-3 body-1">Search for offices held at active and historical BC companies</h4>
    <SearchInput :query.sync="searchQuery" class="mt-10"></SearchInput>

    <div class="d-flex justify-end">
      <SbcButton title="Search"></SbcButton>
    </div>

    <h5>Advanced Search</h5>
  </div>
</template>

<script>
import SearchInput from "@/components/Search/SearchInput.vue";
import SbcButton from "@/components/SbcButton.vue";
export default {
  components: {
    SearchInput,
    SbcButton
  },

  data() {
    return {
      searchQuery: null
    };
  }
};
</script>
