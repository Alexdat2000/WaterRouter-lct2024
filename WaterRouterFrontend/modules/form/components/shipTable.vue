<script setup lang="ts">
import type { Ship } from "../types";
const model = defineModel<Ship[]>();

function isValidDate(d: string) {
  if (!/^\d{4}\/\d{2}\/\d{2}$/.test(d)) return false;
  const year = Number(d.substring(0, 4));
  const month = Number(d.substring(5, 7));
  const day = Number(d.substring(8, 10));
  const date = new Date(year, month - 1, day);
  if (
    isNaN(date.valueOf()) ||
    date.getFullYear() !== year ||
    date.getMonth() + 1 !== month ||
    date.getDate() !== day
  ) {
    return false;
  }
  return true;
}
</script>

<template>
  <table>
    <tr>
      <th>Название</th>
      <th>Откуда</th>
      <th>Куда</th>
      <th>Дата (ГГГГ/ММ/ДД)</th>
      <th>Скорость</th>
      <th>Класс</th>
    </tr>
    <tr v-for="(ship, index) in model">
      <td><input type="text" v-model="ship.name" /></td>
      <td>
        <input type="text" v-model="ship.from" />
      </td>
      <td>
        <input type="text" v-model="ship.to" />
      </td>
      <td :class="{ invalid: !isValidDate(ship.date) }">
        <input type="text" v-model="ship.date" />
      </td>
      <td><input type="number" v-model="ship.speed" /></td>
      <td :class="{ invalid: ship.class < 0 || ship.class > 7 }">
        <select v-model="ship.class">
          <option v-for="i in [...Array(8).keys()]">{{ i }}</option>
        </select>
      </td>
      <td class="rem">
        <NuxtImg
          src="https://img.icons8.com/?size=100&id=3062&format=png&color=000000"
          width="30"
          @click="model?.splice(index, 1)"
        />
      </td>
    </tr>
  </table>
  <button
    @click="
      model?.push({ name: '', from: '', to: '', date: '', speed: 0, class: 0 })
    "
    class="add"
  >
    Добавить заявку
  </button>
</template>

<style scoped lang="scss">
.invalid {
  border: 1px solid red;
}

table {
  margin-right: 20px;
  border-collapse: collapse;
  border-radius: 10px;
  margin-bottom: 8px;
}

td {
  padding: 4px;
  border: 1px solid black;
}

td select {
  width: 100%;
  align-self: center;
  cursor: pointer;
  background-color: transparent;
  border-radius: 100px;
  padding: 10px;
  color: black;
  font-family: Rosatom;
  border: none;
  font-size: 13px;
}

.add {
  width: 10%;
  align-self: center;
  cursor: pointer;
  background-color: #29609f;
  border-radius: 100px;
  padding: 10px;
  color: white;
  font-family: Rosatom;
  font-weight: 600;
  border: none;
  font-size: 13px;
  margin-bottom: 8px;
}

.rem {
  border: none;
}

input {
  width: 100%;
  border: none;
}

input:focus {
  outline: none;
}
</style>
