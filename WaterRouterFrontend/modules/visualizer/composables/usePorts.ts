import type { Port } from "../types";

const ports = reactive<Port[]>([]);

export default function usePorts() {
    onMounted(() => {
        nextTick(async () => {
            ports.length = 0
            const { data } = await useCustomFetch("/getPoints", {
                method: "GET",
                params: {
                    lazy: true
                }
            })
            const result: Port[] = JSON.parse(data.value as string)
            for (const port of result) {
                ports.push(port)
            }
        })
    })
    return { ports }
}
