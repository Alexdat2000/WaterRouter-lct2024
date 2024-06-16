// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  app: {
    head: {
      title: "WaterRouter",
      link: [
        { rel: "icon", href: "/rosatom.ico" },
      ],
    },
  },
  css: ["@/assets/css/main.css"],
  devtools: { enabled: false },
  modules: [
    "~/modules/form",
    "~/modules/visualizer",
    "@nuxt/image",
    "@vueuse/nuxt",
  ],
  runtimeConfig: {
    public: {
      baseURL: process.env.BASE_URL,
    },
  },
});
