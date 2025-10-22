import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "@/App.vue";
const app = createApp(App);
const pinia = createPinia();
app.use(pinia);
// import { initStore } from "./modules/init";
// const init = initStore();
// export { init };
