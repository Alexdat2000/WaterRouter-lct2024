import type { Result, ShipInfo } from "./index";

const dates = reactive<string[]>([]);
const date_ships = reactive<Map<string, ShipInfo[]>>(new Map());
const date_map_id = reactive<Map<string, string>>(new Map());
const gantt_info = ref<string>("");
const routes_info = ref<string>("");
const ships_list = ref<string[]>([]);

const routes_error = ref<string>("");

export default function useRoutes(id?: Ref<string>) {
    if (id) {
        onMounted(() => {
            nextTick(async () => {
                routes_error.value = "";
                routes_info.value = ""
                dates.length = 0
                date_ships.clear()
                date_map_id.clear()

                const { data, error } = await useCustomFetch("/getResult", {
                    method: "GET",
                    params: {
                        id: id.value as string,
                        lazy: true
                    },
                    onResponseError({ response }) {
                        if (response.status == 400) {
                            routes_error.value = response._data as string;
                        }
                        else if (response.status == 404) {
                            routes_error.value = "Расчета с таким id не существует";
                        }
                        else {
                            routes_error.value = "Неизвестная ошибка";
                        }
                    },
                    timeout: 1000 * 60 * 10,
                })

                if (error.value) {
                    return;
                }

                const result: Result = JSON.parse(data.value as string)

                for (const date_info of result.visual_map) {
                    console.log(date_info)
                    dates.push(date_info.date)
                    date_ships.set(date_info.date, date_info.infos)
                    date_map_id.set(date_info.date, date_info.map_id)
                }
                gantt_info.value = result.gantt
                routes_info.value = result.info
                ships_list.value = result.ships
            })
            watch(id, async (newId, oldId) => {
                if (newId !== oldId) {
                    routes_error.value = "";
                    routes_info.value = ""
                    dates.length = 0
                    date_ships.clear()
                    date_map_id.clear()

                    const { data, error } = await useCustomFetch("/getResult", {
                        method: "GET",
                        params: {
                            id: id.value as string,
                            lazy: true
                        },
                        onResponseError({ response }) {
                            if (response.status == 400) {
                                routes_error.value = response._data as string;
                            }
                            else if (response.status == 404) {
                                routes_error.value = "Расчета с таким id не существует";
                            }
                            else {
                                routes_error.value = "Неизвестная ошибка";
                            }
                        },
                        timeout: 1000 * 60 * 10,
                    })

                    if (error.value) {
                        return;
                    }

                    const result: Result = JSON.parse(data.value as string)

                    for (const date_info of result.visual_map) {
                        console.log(date_info)
                        dates.push(date_info.date)
                        date_ships.set(date_info.date, date_info.infos)
                        date_map_id.set(date_info.date, date_info.map_id)
                    }
                    gantt_info.value = result.gantt
                    routes_info.value = result.info
                    ships_list.value = result.ships
                }
            })
        })
    }
    return { dates, date_ships, date_map_id, gantt_info, routes_info, routes_error, ships_list };
}
