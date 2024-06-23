<script setup>
useHead({
  bodyAttrs: {
    style: "margin: 0;",
  },
});
// import component
import VueSlider from "vue-slider-component/dist-css/vue-slider-component.umd.min.js";
import "vue-slider-component/dist-css/vue-slider-component.css";

// import theme
import "vue-slider-component/theme/default.css";

const id = computed(() => useRoute().query.id);
const {
  dates,
  date_ships,
  date_map_id,
  routes_info,
  routes_error,
  ships_list,
} = useRoutes(id);

const tracked_ship = ref("");
provide("tracked_ship", tracked_ship);

const current_date = ref("");
watch(dates, async (newDates, oldDates) => {
  if (current_date.value == "" && newDates.length > 0) {
    current_date.value = newDates[0];
  }
});

async function ganttShips() {
  await navigateTo("http://water.fvds.ru:5000/ganttShips?id=" + id.value, {
    external: true,
  });
}

async function ganttIceships() {
  await navigateTo("http://water.fvds.ru:5000/ganttIceShips?id=" + id.value, {
    external: true,
  });
}
</script>

<template>
  <link
    v-for="date in Array.from(date_map_id.values()).filter(
      (v, i, a) => a.indexOf(v) === i
    )"
    rel="prefetch"
    as="image"
    :href="`${$config.public.baseURL}/getMap?id=${id}&mapid=${date}`"
  />
  <RosatomHeader is-results />
  <div class="error-container" v-if="routes_error">
    <div class="error-middle">
      <NuxtImg
        src="https://img.icons8.com/?size=100&id=3062&format=png&color=FA5252"
        width="100"
        height="100"
      />
      <h2>{{ routes_error }}</h2>
      <div class="buttons">
        <button
          v-if="routes_error != 'Расчета с таким id не существует'"
          @click="
            routes_error = '';
            navigateTo('/?id=' + id);
          "
          style="width: 300px"
        >
          Назад
        </button>
        <button v-else style="width: 300px" @click="navigateTo('/')">
          Новый расчет
        </button>
      </div>
    </div>
  </div>
  <Loading v-else-if="!dates.length" />
  <div class="page" v-else>
    <div
      style="
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        height: 100%;
        width: 100%;
      "
    >
      <p v-if="routes_info" class="routes_info" v-html="routes_info"></p>
      <div class="buttons">
        <button @click="ganttShips">Диаграмма Ганта заявок</button>
        <button @click="ganttIceships">Диаграмма Ганта ледоколов</button>
        <a :href="'http://water.fvds.ru:5000/getRawData?id=' + id" download>
          Скачать маршрутные данные
        </a>
      </div>
      <div class="track">
        <p>Отслеживать корабль:</p>
        <select v-model="tracked_ship">
          <option v-for="ship in ships_list">{{ ship }}</option>
        </select>
      </div>
      <vue-slider
        style="width: 50vw"
        :data="dates"
        v-model="current_date"
      ></vue-slider>
      <h2>{{ current_date }}</h2>
      <div style="position: relative; width: 80%">
        <NuxtImg
          v-if="date_map_id.get(current_date)"
          :src="`${
            $config.public.baseURL
          }/getMap?id=${id}&mapid=${date_map_id.get(current_date)}`"
          style="
            position: relative;
            left: 0;
            top: 0;
            width: 100%;
            height: calc(var(width) / 2);
          "
        />
        <ShipMap :ship_infos="date_ships.get(current_date)" />
        <PathCanvas :date_ships="date_ships.get(current_date)" />
        <PortTooltips />
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.track {
  display: flex;
  flex-direction: row;
  gap: 10px;
  font-size: 16px;
  font-weight: bold;
  max-width: 80%;
  height: 41px;
  align-items: center;
  margin-bottom: 15px;
  margin-top: 7px;  
}

.track select {
  font-size: 16px;
  font-weight: bold;
  border-radius: 100px;
  border: none;
  background-color: #29609f;
  color: white;
  padding-left: 10px;
  height: 100%;
  appearance: none;
  background-image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAAACXBIWXMAAAsTAAALEwEAmpwYAAABUElEQVR4nO3UMU4DMRCF4TlHLgMSaSlzGmhJqlfQIM5KwUMRixQlBURk7bHn/yRLK22xs/4tRwAAAAAAAAAAAAAAAAAAAAAAAAAAAFzJ9sb2o+0dy7tlLzZdDpLtZ9sfxrnjnjy1jrG9GAPnti2DvF98HufeCFI4CFfW7x6aBVmiHP4wVFWHpjFOorz0/vOE1CUGURLGIErCGD+KX1+KjIpGUWRWLIpiBEWiKEYyeRTFiCaNohjZZFEUM5gkimImg0dRzGjQKIqZDRZFUcEgURSVJI+iqChpFEVlyaKo936kkCSKeu9DKp2jqPf/p+Q+UYiRKIqanbaRuU0UYiSKotVO08y8ThRiJIqim52WynybKMRIFEU3HQb/ikKMRFG06jC4KgoxEkVR02Hwzfbe9udJiOPzfnmNHmzf235d1h0VAAAAAAAAAAAAAAAAAERfX6MjL5dyvtIeAAAAAElFTkSuQmCC);
  background-size: 20px;
  background-position: 95%;
  background-repeat: no-repeat;
}

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

.buttons {
  width: 100%;
  display: flex;
  justify-content: center;
  gap: 10px;
}

.buttons button,
.buttons a {
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

a {
  all: unset;
}

.routes_info {
  font-size: 20px;
  font-weight: bold;
  max-width: 80%;
}

.page {
  margin-top: 20px;
  width: 100vw;
  // height: calc(100vh - 82.5px);
  font-family: Rosatom;
}
</style>
