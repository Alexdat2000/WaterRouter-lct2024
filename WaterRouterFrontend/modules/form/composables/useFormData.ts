import type { Form } from "../types";

let formData = ref({} as Form);
const formLoaded = ref(false);
const formLoadingError = ref("");

async function refetch(id: string) {
    formLoadingError.value = "";
    formData.value = {} as Form
    formLoaded.value = false
    const { data, error } = await useCustomFetch("/getFormInfo", {
        method: "GET",
        params: {
            id: id,
            lazy: true
        },
        onResponseError({ response }) {
            if (response.status == 400) {
                formLoadingError.value = response._data as string;
            } else if (response.status == 404) {
                formLoadingError.value = "Формы с таким id не существует";
            } else {
                formLoadingError.value = "Неизвестная ошибка, попробуйте снова";
            }
        },
        watch: false,
    })
    if (error.value) {
        return;
    }
    console.log(data.value as string)
    formData.value = JSON.parse(data.value as string)
    formLoaded.value = true
}

export default async function useFormData(id: string) {
    onMounted(() => {
        nextTick(async () => {
            formLoadingError.value = "";
            formData.value = {} as Form
            formLoaded.value = false
            const { data, error } = await useCustomFetch("/getFormInfo", {
                method: "GET",
                params: {
                    id: id,
                    lazy: true
                },
                onResponseError({ response }) {
                    if (response.status == 400) {
                        formLoadingError.value = response._data as string;
                    } else if (response.status == 404) {
                        formLoadingError.value = "Формы с таким id не существует";
                    } else {
                        formLoadingError.value = "Неизвестная ошибка, попробуйте снова";
                    }
                },
                watch: false,
            })
            if (error.value) {
                return;
            }
            console.log(data.value as string)
            formData.value = JSON.parse(data.value as string)
            formLoaded.value = true
        })
    });
    return { formData, formLoaded, refetch, formLoadingError }
}
