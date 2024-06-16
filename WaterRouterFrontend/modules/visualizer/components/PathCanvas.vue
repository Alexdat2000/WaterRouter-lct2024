<script setup lang="ts">
import type { ShipInfo } from "../types";

const props = defineProps<{ date_ships?: ShipInfo[] }>();

const canvas = ref<HTMLCanvasElement>();
const ctx = ref<CanvasRenderingContext2D>();

function canvas_arrow(
  context: CanvasRenderingContext2D,
  fromx: number,
  fromy: number,
  tox: number,
  toy: number
) {
  var headlen = 100;
  var dx = tox - fromx;
  var dy = toy - fromy;
  var angle = Math.atan2(dy, dx);
  context.moveTo(fromx, fromy);
  context.lineTo(tox, toy);
  context.lineTo(
    Math.floor(tox - headlen * Math.cos(angle - Math.PI / 6)),
    Math.floor(toy - headlen * Math.sin(angle - Math.PI / 6))
  );
  context.moveTo(tox, toy);
  context.lineTo(
    Math.floor(tox - headlen * Math.cos(angle + Math.PI / 6)),
    Math.floor(toy - headlen * Math.sin(angle + Math.PI / 6))
  );
}

function draw_paths(
  canvas?: HTMLCanvasElement,
  ctx?: CanvasRenderingContext2D,
  ship_infos?: ShipInfo[]
) {
  console.log(ship_infos);
  if (!canvas || !ctx || !ship_infos) {
    return;
  }
  console.log("drawing");
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.beginPath();
  for (const ship_info of ship_infos) {
    canvas_arrow(
      ctx,
      Math.floor((ship_info.from_x / 1000) * canvas.width),
      Math.floor((ship_info.from_y / 500) * canvas.height),
      Math.floor((ship_info.to_x / 1000) * canvas.width),
      Math.floor((ship_info.to_y / 500) * canvas.height)
    );
  }
  ctx.strokeStyle = "#ff715b";
  ctx.lineWidth = 15;
  ctx.stroke();
  ctx.closePath();
}

onMounted(() => {
  canvas.value = document.getElementById("paths") as HTMLCanvasElement;
  ctx.value = canvas.value.getContext("2d") as CanvasRenderingContext2D;
  //   draw_paths(canvas.value, ctx.value, date_ships.value);
  draw_paths(canvas.value, ctx.value, props.date_ships);
});

watch(
  () => props.date_ships,
  (newDateShips, oldDateShips) => {
    console.log("meow");
    draw_paths(canvas.value, ctx.value, newDateShips);
  },
  { deep: true }
);
</script>

<template>
  <canvas
    width="10000"
    height="5000"
    id="paths"
    style="
      z-index: 1;
      position: absolute;
      left: 0;
      top: 0;
      width: 100%;
      height: 100%;
    "
  ></canvas>
</template>
