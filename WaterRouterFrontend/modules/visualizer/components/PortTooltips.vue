<script setup lang="ts">
import { directive as vTippy } from "vue-tippy";
import "tippy.js/dist/tippy.css";
import "tippy.js/themes/material.css";

const { ports } = usePorts();
</script>

<template>
  <div
    v-for="port in ports"
    :style="`z-index: 10; position: absolute; left: ${port.x / 10}%; top: ${
      port.y / 5
    }%; width: 30px; height: 30px; transform: translate(-50%, -50%);`"
    v-tippy="{
      content: `${port.name}`,
      allowHTML: true,
      theme: 'material',
    }"
  />
</template>
