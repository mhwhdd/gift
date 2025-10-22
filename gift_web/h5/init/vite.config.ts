import { fileURLToPath, URL } from "node:url";
import { defineConfig, loadEnv } from "vite";
import vue from "@vitejs/plugin-vue";
import { VantResolver } from "unplugin-vue-components/resolvers";
import Components from "unplugin-vue-components/vite";
import viteCompression from "vite-plugin-compression";
import postcsspxtoviewport from "postcss-px-to-viewport";
const serverIp = "https://whalesing.imai.site"; //转发测试服
const basePath = "/init/";
// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  process.env = Object.assign(process.env, loadEnv(mode, process.cwd(), ""));
  return {
    publicDir: "public",
    base: basePath,
    server: {
      /** 是否开启 https */
      https: false,
      /** host 设置为 true 才可以使用 network 的形式，以 ip 访问项目 */
      host: true, // host: "0.0.0.0"
      /** 端口号 */
      port: 3333,
      /** 是否自动打开浏览器 */
      open: false,
      /** 跨域设置允许 */
      cors: true,
      /** 端口被占用时，是否直接退出 */
      strictPort: false,
      /** 接口代理 */
      proxy: {
        "/tomsg": {
          target: serverIp + "/tomsg",
          ws: true,
          /** 是否允许跨域 */
          changeOrigin: true,
          secure: false,
          rewrite: (path: any) => path.replace("/tomsg", ""),
        },
      },
    },
    build: {
      outDir: process.env.npm_lifecycle_event?.startsWith("build-release")
        ? "release"
        : "dist",
      /** 消除打包大小超过 500kb 警告 */
      chunkSizeWarningLimit: 2000,
      rollupOptions: {
        output: {
          assetFileNames: (info) => {
            // 生成唯一的文件名
            return `assets/[name]-[hash].[ext]`;
          },
          chunkFileNames: (info) => {
            // 生成唯一的文件名
            return `static/[name]-[hash].js`;
          },
          entryFileNames: (info) => {
            // 生成唯一的文件名
            const timestamp = new Date().getTime();
            return `static/[name]-${timestamp}.js`;
          },
        },
      },
      /** Vite 2.6.x 以上需要配置 minify: "terser", terserOptions 才能生效 */
      minify: "terser",
      /** 在打包代码时移除 console.log、debugger 和 注释 */
      // terserOptions: {
      //   compress: {
      //     drop_console: false,
      //     drop_debugger: true,
      //     pure_funcs: ['console.log']
      //   },
      //   format: {
      //     /** 删除注释 */
      //     comments: false
      //   }
      // },
      /** 打包后静态资源目录，区别静态源目录使用assets目录 */
      assetsDir: "static",
    },
    plugins: [
      vue(),
      Components({
        resolvers: [VantResolver()],
      }),
      viteCompression({
        //生成压缩包gz
        verbose: true, // 输出压缩成功
        disable: false, // 是否禁用
        threshold: 20 * 1024, // 体积大于阈值会被压缩，单位是b
        algorithm: "gzip", // 压缩算法
        ext: ".gz", // 生成的压缩包后缀
      }),
    ],
    css: {
      preprocessorOptions: {
        scss: {
          additionalData: `@import "@/style/common.scss";`,
        },
      },
      postcss: {
        plugins: [
          postcsspxtoviewport({
            unitToConvert: "px",
            viewportWidth: 375,
            unitPrecision: 6,
            propList: ["*"],
            viewportUnit: "vw",
            fontViewportUnit: "vw",
            selectorBlackList: ["ignore-"],
            minPixelValue: 1,
            mediaQuery: false,
            replace: true,
            exclude: [/^(?!.*node_modules\/vant)/],
            landscape: false,
          }),
          postcsspxtoviewport({
            // 要转化的单位
            unitToConvert: "px",
            // UI设计稿的大小
            viewportWidth: 750,
            // 转换后的精度
            unitPrecision: 6,
            // 转换后的单位
            viewportUnit: "vw",
            // 字条转换后的单位
            fontViewportUnit: "vw",
            // 能转换的属性，*表示所有属性，!border表示border不转
            propList: ["*"],
            // 指定不转换为视窗单位的类名，
            selectorBlackList: ["ignore-"],
            // 最小转换的值，小于等于1不转
            minPixelValue: 1,
            // 是否在媒体查询的css代码中也进行转换，默认false
            mediaQuery: false,
            // 是否转换后直接更换属性值
            replace: true,
            // 忽略某些文件夹下的文件或特定文件，例如 'node_modules' 下的文件
            exclude: [],
            // 包含那些文件或者特定文件
            include: [],
            // 是否处理横屏情况
            landscape: false,
          }),
        ],
      },
    },
    resolve: {
      alias: {
        "@": fileURLToPath(new URL("./src", import.meta.url)),
      },
    },
  };
});
