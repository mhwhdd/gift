<template>
  <router-view v-slot="{ Component }" ref="main">
    <transition name="slide-left">
      <keep-alive>
        <component :is="Component" v-if="route.meta.keepAlive" />
      </keep-alive>
    </transition>
    <component :is="Component" v-if="!route.meta.keepAlive" />
  </router-view>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { useRoute } from "vue-router";
const route = useRoute();
onMounted(async () => {});
</script>
<style></style>
<style>
img {
  /* 设置图片在ios上点击不能放大预览 */
  -webkit-touch-callout: none !important;
}
</style>
