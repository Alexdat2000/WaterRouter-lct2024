<script setup lang="ts">
useHead({
  bodyAttrs: {
    style: "margin: 0;",
  },
});

const id = computed(() => useRoute().query.id);

const { formData, formLoaded, refetch, formLoadingError } = await useFormData(
  id.value as string
);

watch(id, async (newId, oldId) => {
  if (newId != oldId) {
    await refetch(newId as string);
  }
});

const shipsUploading = ref(false);
const shipsTableEditing = ref(false);
const shipsFileField = ref();
const shipsUploadingError = ref("");

const shipsTableError = ref("");
const iceshipsTableError = ref("");

const shipsFileLoading = ref(false);
const shipsTableLoading = ref(false);
const iceshipsTableLoading = ref(false);
const iceFileLoading = ref(false);

watch(
  formData,
  () => {
    shipsTableError.value = "";
    iceshipsTableError.value = "";
  },
  { deep: true }
);

watch(shipsFileField, () => {
  shipsUploadingError.value = "";
});

const iceFileField = ref();
const iceUploading = ref(false);
const iceUploadingError = ref("");

watch(iceFileField, () => {
  iceUploadingError.value = "";
});

const iceshipTableEditing = ref(false);

async function uploadShipsFile() {
  shipsFileLoading.value = true;
  const file = shipsFileField.value.files[0];
  const formFile = new FormData();
  formFile.append("id", id.value as string);
  formFile.append("file", file);
  const { data, error } = await useCustomFetch("/submitApplicationsXlsx", {
    method: "POST",
    body: formFile,
    onResponseError({ response }) {
      if (response.status == 400) {
        shipsUploadingError.value = response._data as string;
      } else {
        shipsUploadingError.value = "Неизвестная ошибка, попробуйте снова";
      }
    },
    watch: false,
  });
  shipsFileLoading.value = false;
  if (error.value) {
    return;
  }
  console.log(data);
  formData.value.current_ships = JSON.parse(data.value as string).current_ships;
  shipsUploading.value = false;
}

async function uploadIceFile() {
  iceFileLoading.value = true;
  const file = iceFileField.value.files[0];
  const formFile = new FormData();
  formFile.append("file", file);
  formFile.append("id", id.value as string);
  const { data, error } = await useCustomFetch("/submitIceXlsx", {
    method: "POST",
    body: formFile,
    onResponseError({ response }) {
      if (response.status == 400) {
        iceUploadingError.value = response._data as string;
      } else {
        iceUploadingError.value = "Неизвестная ошибка, попробуйте снова";
      }
    },
    watch: false,
  });
  iceFileLoading.value = false;
  if (error.value) {
    return;
  }
  console.log(data);
  formData.value.ice_filename = data.value as string;
  iceUploading.value = false;
}

async function uploadIceships() {
  iceshipsTableLoading.value = true;
  const { data, error } = await useCustomFetch("/submitIceships", {
    method: "POST",
    body: {
      id: id.value as string,
      data: formData.value.iceships,
      iceships_date: formData.value.iceships_date,
    },
    onResponseError({ response }) {
      if (response.status == 400) {
        iceshipsTableError.value = response._data as string;
      } else {
        iceshipsTableError.value = "Неизвестная ошибка, попробуйте снова";
      }
    },
    watch: false,
  });
  iceshipsTableLoading.value = false;
  if (error.value) {
    return;
  }
  iceshipTableEditing.value = false;
}

async function uploadShips() {
  shipsTableLoading.value = true;
  const { data, error } = await useCustomFetch("/submitApplicationsTable", {
    method: "POST",
    body: {
      id: id.value as string,
      current_ships: formData.value.current_ships,
    },
    onResponseError({ response }) {
      if (response.status == 400) {
        shipsTableError.value = response._data as string;
      } else {
        shipsTableError.value = "Неизвестная ошибка, попробуйте снова";
      }
    },
    watch: false,
  });
  shipsTableLoading.value = false;
  if (error.value) {
    return;
  }
  shipsTableEditing.value = false;
}

const formValid = computed(() => {
  return (
    formData.value.current_ships.length > 0 &&
    formData.value.iceships.length > 0 &&
    formData.value.ice_filename != "" &&
    shipsUploading.value == false &&
    shipsTableEditing.value == false &&
    iceUploading.value == false &&
    iceshipTableEditing.value == false
  );
});

async function submitForm() {
  await useCustomFetch("/runCalc", {
    method: "GET",
    params: {
      id: id.value as string,
      lazy: true,
    },
  });
  navigateTo(`/result?id=${id.value as string}`);
}
</script>

<template>
  <RosatomHeader />
  <div class="error-container" v-if="formLoadingError">
    <div class="error-middle">
      <NuxtImg
        src="https://img.icons8.com/?size=100&id=3062&format=png&color=FA5252"
        width="100"
        height="100"
      />
      <h2>{{ formLoadingError }}</h2>
      <button
        style="width: 300px"
        class="error-button"
        @click="
          formLoadingError = '';
          navigateTo('/');
        "
      >
        Новый расчет
      </button>
    </div>
  </div>
  <div v-else-if="formLoaded" class="page">
    <div class="section">
      <h2>Заявки</h2>
      <template v-if="shipsUploading">
        <p class="error" v-if="shipsUploadingError">
          {{ shipsUploadingError }}
        </p>
        <div v-show="!shipsFileLoading" class="file_upload">
          <button @click="shipsUploading = false">Назад</button>
          <input type="file" ref="shipsFileField" accept=".xlsx" />
          <button @click="uploadShipsFile">Загрузить</button>
        </div>
        <NuxtImg
          v-if="shipsFileLoading"
          src="https://img.icons8.com/?size=100&id=gGiE9u2aJPFz&format=png&color=000000"
          class="spinner"
          width="33"
          height="33"
        />
      </template>
      <template v-else-if="shipsTableEditing">
        <ShipTable v-model="formData.current_ships" />
        <p style="align-self: center" class="error" v-if="shipsTableError">
          {{ shipsTableError }}
        </p>
        <button class="save" @click="uploadShips">Сохранить</button>
      </template>
      <template v-else>
        {{ formData.current_ships.length }} корабля(ей) введено
        <div class="buttons">
          <button @click="shipsUploading = true">Загрузить новый файл</button>
          <button @click="shipsTableEditing = true">Редактировать</button>
        </div>
      </template>
    </div>
    <div class="section">
      <h2>Ледоколы</h2>
      <template v-if="iceshipTableEditing">
        <IceshipTable
          v-model:iceships="formData.iceships"
          v-model:date="formData.iceships_date"
        />
        <p style="align-self: center" class="error" v-if="iceshipsTableError">
          {{ iceshipsTableError }}
        </p>
        <button
          v-if="!iceshipsTableLoading"
          class="save"
          @click="uploadIceships"
        >
          Сохранить
        </button>
        <NuxtImg
          v-else
          style="align-self: center"
          src="https://img.icons8.com/?size=100&id=gGiE9u2aJPFz&format=png&color=000000"
          class="spinner"
          width="33"
          height="33"
        />
      </template>
      <template v-else>
        {{ formData.iceships.length }} ледокола(ов) введено
        <div class="buttons">
          <button @click="iceshipTableEditing = true">Редактировать</button>
        </div>
      </template>
    </div>
    <div>
      <h2>Таблица с информацией о ледовых условиях</h2>
      <template v-if="iceUploading">
        <p class="error" v-if="iceUploadingError">{{ iceUploadingError }}</p>
        <div v-if="!iceFileLoading" class="file_upload">
          <button @click="iceUploading = false">Назад</button>
          <input type="file" ref="iceFileField" accept=".xlsx" />
          <button @click="uploadIceFile">Загрузить</button>
        </div>
        <NuxtImg
          v-else
          class="spinner"
          src="https://img.icons8.com/?size=100&id=gGiE9u2aJPFz&format=png&color=000000"
          width="33"
          height="33"
        />
      </template>
      <template v-else>
        <div class="section">
          {{ formData.ice_filename }}
          <div class="buttons">
            <button @click="iceUploading = true">Загрузить новый файл</button>
          </div>
        </div>
      </template>
    </div>
    <div class="submit">
      <button v-if="!formValid" disabled>Заполните все поля</button>
      <button v-else @click="submitForm">Запустить расчет</button>
    </div>
  </div>
  <Loading v-else />
</template>

<style scoped lang="scss">
.error-container {
  width: 100vw;
  height: calc(100vh - 82.5px);
  display: flex;
  align-items: center;
  justify-content: center;
}

.error-middle {
  font-family: Rosatom;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.error-button {
  cursor: pointer;
  background-color: #29609f;
  border-radius: 100px;
  padding: 10px;
  color: white;
  font-family: Rosatom;
  font-weight: 600;
  border: none;
  font-size: 16px;
  margin-bottom: 8px;
}

.spinner {
  animation: spin 2s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.error {
  color: #ff0000;
  font-size: 14px;
  font-weight: 600;
}

.submit {
  margin-top: 20px;
}

.submit button {
  width: 300px;
  cursor: pointer;
  background-color: #29609f;
  border-radius: 100px;
  padding: 10px;
  color: white;
  font-family: Rosatom;
  font-weight: 600;
  border: none;
  font-size: 13px;
}

.submit button:disabled {
  cursor: not-allowed;
  background: transparent;
  color: black;
  border: 1px solid black;
}

.file_upload {
  display: flex;
  flex-direction: row;
  gap: 5px;
}

.file_upload button {
  cursor: pointer;
  background-color: #29609f;
  border-radius: 100px;
  padding: 10px;
  color: white;
  font-family: Rosatom;
  font-weight: 600;
  border: none;
  font-size: 13px;
}

.file_upload input {
  height: 100%;
  align-content: center;
}

.file_upload input[type="file"]::file-selector-button {
  margin-right: 10px;
  cursor: pointer;
  background-color: #29609f;
  border-radius: 100px;
  padding: 10px;
  color: white;
  font-family: Rosatom;
  font-weight: 600;
  border: none;
  font-size: 13px;
}

body {
  margin: 0;
}

.page {
  padding: 10px;
  padding-left: 20px;
  width: 100%;
  font-family: Rosatom;
}

.section {
  display: flex;
  flex-direction: column;
}

.section .buttons {
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
  gap: 10px;
  margin-top: 10px;
}

.section .buttons button {
  cursor: pointer;
  background-color: #29609f;
  border-radius: 100px;
  padding: 10px;
  color: white;
  font-family: Rosatom;
  font-weight: 600;
  border: none;
  font-size: 13px;
}

.save {
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
</style>
