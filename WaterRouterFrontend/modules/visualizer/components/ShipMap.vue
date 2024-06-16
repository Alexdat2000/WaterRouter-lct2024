<script setup lang="ts">
import type { ShipInfo } from "../types";
defineProps<{ ship_infos?: ShipInfo[] }>();
</script>

<template>
  <Ship
    v-for="(ship_info, index) in ship_infos"
    :ship_info="ship_info"
    :z_layer="10 + index"
  />
</template>
