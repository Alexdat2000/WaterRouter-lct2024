<script setup lang="ts">
const props = defineProps<{ isResults?: boolean }>();
const id = useRoute().query.id as string;

async function clone() {
  const { data } = await useCustomFetch("/newFromExisting", {
    method: "GET",
    params: {
      id: id,
    },
  });
  const { refetch } = await useFormData(id);
  await refetch(data.value as string);
  await navigateTo("/?id=" + data.value);
}

async function newId() {
  const { data } = await useCustomFetch("/new", {
    method: "GET",
  });
  const { refetch } = await useFormData(id);
  await refetch(data.value as string);
  await navigateTo("/?id=" + data.value);
}

async function newFromTemplate() {
  const { data } = await useCustomFetch("/newFromTemplate", {
    method: "GET",
  });
  const { refetch } = await useFormData(id);
  await refetch(data.value as string);
  await navigateTo("/?id=" + data.value);
}

async function edit() {
  const { refetch } = await useFormData(id);
  await refetch(id);
  await navigateTo("/?id=" + id);
}
</script>

<template>
  <header class="header">
    <NuxtImg
      src="https://i.ibb.co/dBMvx23/rosatom-logo.png"
      style="height: 100%"
    />
    <h1 class="name">РОСАТОМ</h1>
    <div class="buttons">
      <button v-if="isResults" @click="edit" class="button">
        Редактировать
      </button>
      <button @click="newId" class="button">Новый расчет</button>
      <button @click="newFromTemplate" class="button">Новый из шаблона</button>
      <button @click="clone" class="button">Дублировать</button>
    </div>
  </header>
</template>

<style scoped lang="scss">
.header {
  width: 100%;
  top: 0;
  left: 0;
  background: white;
  z-index: 100;
  padding: 15px;
  display: flex;
  flex-direction: row;
  align-items: center;
  height: 50px;
  border-bottom: 3px solid black;
}

.name {
  margin-left: 10px;
  font-family: Rosatom;
}

.buttons {
  margin-right: 15px;
  padding: 15px;
  height: 100%;
  display: flex;
  flex-direction: row;
  align-items: center;
  margin-left: auto;
  gap: 10px;
}

.button {
  cursor: pointer;
  height: 100%;
  background-color: #29609f;
  border-radius: 100px;
  padding: 15px;
  color: white;
  font-family: Rosatom;
  font-weight: 600;
  border: none;
  font-size: 16px;
}
</style>
