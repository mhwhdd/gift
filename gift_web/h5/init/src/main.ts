import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";
import router from "./router";
import { Toast, Dialog } from "vant";
import "vant/es/toast/style";
import "vant/es/dialog/style";
const pinia = createPinia();
const app = createApp(App);
app.use(pinia).use(router).use(Toast).use(Dialog).mount("#app");

import Vconsole from "vconsole";
let v: any = null;
if (import.meta.env.VITE_USER_NODE_ENV === "test") {
  v = new Vconsole();
}
export default v;
