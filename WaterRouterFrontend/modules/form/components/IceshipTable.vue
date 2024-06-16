<script setup lang="ts">
import type { Iceship } from "../types";
const iceships = defineModel<Iceship[]>("iceships");
const date = defineModel<string>("date");

function isValidDate(d?: string) {
  if (!d) return false;
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
  <div class="date_input">
    <h4>Дата: (ГГГГ/ММ/ДД)</h4>
    <input
      type="text"
      v-model="date"
      :class="{ invalid: !isValidDate(date) }"
    />
  </div>
  <table>
    <tr>
      <th>Название</th>
      <th>Изначальное положение</th>
      <th>Собственная скорость</th>
      <th>Штраф % при тяжести 19-15</th>
      <th>Штраф % при тяжести 14-10</th>
    </tr>
    <tr v-for="(iceship, index) in iceships">
      <td><input type="text" v-model="iceship.name" /></td>
      <td>
        <input type="text" v-model="iceship.location" />
      </td>
      <td><input type="number" v-model="iceship.sp3" /></td>
      <td :class="{ invalid: iceship.fine2 < 0 || iceship.fine2 > 100 }">
        <input type="number" v-model="iceship.fine2" min="0" max="100" />
      </td>
      <td :class="{ invalid: iceship.fine1 < 0 || iceship.fine1 > 100 }">
        <input type="number" v-model="iceship.fine1" min="0" max="100" />
      </td>
      <td class="rem">
        <NuxtImg
          src="https://img.icons8.com/?size=100&id=3062&format=png&color=000000"
          width="30"
          @click="iceships?.splice(index, 1)"
        />
      </td>
    </tr>
  </table>
  <button
    @click="
      iceships?.push({ name: '', location: '', sp3: 0, fine1: 0, fine2: 0 })
    "
    class="add"
  >
    Добавить ледокол
  </button>
</template>

<style scoped lang="scss">
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

.invalid {
  border: 1px solid red !important;
}

.date_input {
  display: flex;
  flex-direction: column;
  margin-bottom: 20px;
}

.date_input input {
  margin-top: -5px;
  width: 73px;
  font-weight: 600;
  font-size: 14px;
  border: 1px solid black;
  padding: 15px;
  border-radius: 30px;
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
