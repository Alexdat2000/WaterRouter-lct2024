<script setup lang="ts">
import { directive as vTippy } from "vue-tippy";
import "tippy.js/dist/tippy.css";
import "tippy.js/themes/material.css";

import type { ShipInfo } from "../types";
defineProps<{ ship_info: ShipInfo; z_layer: number }>();

const tracked_ship = inject("tracked_ship") as Ref<string>;
</script>

<template>
  <NuxtImg
    :src="`${$config.public.baseURL}/getIcon?id=${ship_info.ships.includes(tracked_ship) ? ship_info.icon_selected : ship_info.icon}`"
    :style="`z-index: ${z_layer}; position: absolute; left: ${
      ship_info.x / 10
    }%; top: ${ship_info.y / 5}%; 
    height: 50px;
  transform: translate(-50%, -50%);
     `"
    v-tippy="{
      content: `${ship_info.tooltip}`,
      allowHTML: true,
      theme: 'material',
    }"
  />
</template>

<style>
.tippy-box {
  font-family: "Rosatom" !important;
}
</style>
