export default defineNuxtRouteMiddleware(async (to, from) => {
    if (!to.query.id) {
        let id = "";
        const { data } = await useCustomFetch("/new", { method: "GET" });
        id = data.value as string;
        return navigateTo("/?id=" + id, { replace: true });
    }
})
