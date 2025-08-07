// vite.config.ts
import { defineConfig, loadEnv } from "file:///D:/Paksa%20Financial%20System/frontend/node_modules/vite/dist/node/index.js";
import vue from "file:///D:/Paksa%20Financial%20System/frontend/node_modules/@vitejs/plugin-vue/dist/index.mjs";
import { fileURLToPath, URL } from "node:url";
var __vite_injected_original_import_meta_url = "file:///D:/Paksa%20Financial%20System/frontend/vite.config.ts";
var vite_config_default = defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  return {
    css: {
      preprocessorOptions: {
        scss: {
          additionalData: `
            @import "@/assets/scss/_variables.scss";
            @import "@/assets/scss/_mixins.scss";
          `
        }
      }
    },
    base: env.VITE_APP_BASE_URL || "/",
    define: {
      __APP_VERSION__: JSON.stringify(env.VITE_APP_VERSION || "1.0.0"),
      __APP_ENV__: JSON.stringify(mode)
    },
    resolve: {
      alias: [
        { find: "@", replacement: fileURLToPath(new URL("./src", __vite_injected_original_import_meta_url)) },
        { find: /^~(.+)/, replacement: fileURLToPath(new URL("./node_modules/$1", __vite_injected_original_import_meta_url)) },
        { find: "vue", replacement: "vue/dist/vue.esm-bundler.js" },
        { find: "@assets", replacement: fileURLToPath(new URL("./src/assets", __vite_injected_original_import_meta_url)) },
        { find: "@components", replacement: fileURLToPath(new URL("./src/components", __vite_injected_original_import_meta_url)) },
        { find: "@views", replacement: fileURLToPath(new URL("./src/views", __vite_injected_original_import_meta_url)) },
        { find: "@stores", replacement: fileURLToPath(new URL("./src/stores", __vite_injected_original_import_meta_url)) },
        { find: "@utils", replacement: fileURLToPath(new URL("./src/utils", __vite_injected_original_import_meta_url)) },
        { find: "@api", replacement: fileURLToPath(new URL("./src/api", __vite_injected_original_import_meta_url)) },
        { find: "@router", replacement: fileURLToPath(new URL("./src/router", __vite_injected_original_import_meta_url)) }
      ],
      extensions: [".mjs", ".js", ".ts", ".jsx", ".tsx", ".json", ".vue"]
    },
    plugins: [
      vue({
        script: { defineModel: true, propsDestructure: true }
      })
    ],
    server: {
      host: "0.0.0.0",
      port: 3e3,
      strictPort: true,
      open: true,
      headers: {
        "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https:; style-src 'self' 'unsafe-inline' https:; font-src 'self' https: data:; img-src 'self' https://images.unsplash.com https: data: blob:; connect-src 'self' https: ws: wss:;"
      },
      proxy: {
        "/api": {
          target: "http://localhost:8000",
          changeOrigin: true,
          secure: false,
          ws: true,
          rewrite: (path) => path.replace(/^\/api/, "")
        },
        "/auth": {
          target: "http://localhost:8000",
          changeOrigin: true,
          secure: false
        }
      }
    },
    build: {
      outDir: "dist",
      assetsDir: "assets",
      sourcemap: true,
      minify: "terser",
      terserOptions: {
        compress: {
          drop_console: mode === "production",
          drop_debugger: mode === "production"
        }
      },
      rollupOptions: {
        output: {
          manualChunks: {
            vue: ["vue", "vue-router", "pinia"],
            primevue: ["primevue"],
            primeicons: ["primeicons"],
            primeflex: ["primeflex"]
          }
        }
      }
    },
    optimizeDeps: {
      include: [
        "vue",
        "vue-router",
        "pinia",
        "primevue/config",
        "primevue/button",
        "primevue/inputtext",
        "primevue/menu",
        "primevue/sidebar",
        "primevue/inputswitch",
        "primeicons/primeicons.css",
        "primeflex/primeflex.css"
      ]
    },
    ssr: {
      noExternal: ["primevue"]
    }
  };
});
export {
  vite_config_default as default
};
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsidml0ZS5jb25maWcudHMiXSwKICAic291cmNlc0NvbnRlbnQiOiBbImNvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9kaXJuYW1lID0gXCJEOlxcXFxQYWtzYSBGaW5hbmNpYWwgU3lzdGVtXFxcXGZyb250ZW5kXCI7Y29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2ZpbGVuYW1lID0gXCJEOlxcXFxQYWtzYSBGaW5hbmNpYWwgU3lzdGVtXFxcXGZyb250ZW5kXFxcXHZpdGUuY29uZmlnLnRzXCI7Y29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2ltcG9ydF9tZXRhX3VybCA9IFwiZmlsZTovLy9EOi9QYWtzYSUyMEZpbmFuY2lhbCUyMFN5c3RlbS9mcm9udGVuZC92aXRlLmNvbmZpZy50c1wiO2ltcG9ydCB7IGRlZmluZUNvbmZpZywgbG9hZEVudiwgdHlwZSBDb25maWdFbnYgfSBmcm9tICd2aXRlJ1xuaW1wb3J0IHZ1ZSBmcm9tICdAdml0ZWpzL3BsdWdpbi12dWUnXG5pbXBvcnQgeyBmaWxlVVJMVG9QYXRoLCBVUkwgfSBmcm9tICdub2RlOnVybCdcbmV4cG9ydCBkZWZhdWx0IGRlZmluZUNvbmZpZygoeyBtb2RlIH06IENvbmZpZ0VudikgPT4ge1xuICBjb25zdCBlbnYgPSBsb2FkRW52KG1vZGUsIHByb2Nlc3MuY3dkKCksICcnKVxuXG4gIHJldHVybiB7XG4gICAgY3NzOiB7XG4gICAgICBwcmVwcm9jZXNzb3JPcHRpb25zOiB7XG4gICAgICAgIHNjc3M6IHtcbiAgICAgICAgICBhZGRpdGlvbmFsRGF0YTogYFxuICAgICAgICAgICAgQGltcG9ydCBcIkAvYXNzZXRzL3Njc3MvX3ZhcmlhYmxlcy5zY3NzXCI7XG4gICAgICAgICAgICBAaW1wb3J0IFwiQC9hc3NldHMvc2Nzcy9fbWl4aW5zLnNjc3NcIjtcbiAgICAgICAgICBgXG4gICAgICAgIH1cbiAgICAgIH1cbiAgICB9LFxuXG4gICAgYmFzZTogZW52LlZJVEVfQVBQX0JBU0VfVVJMIHx8ICcvJyxcblxuICAgIGRlZmluZToge1xuICAgICAgX19BUFBfVkVSU0lPTl9fOiBKU09OLnN0cmluZ2lmeShlbnYuVklURV9BUFBfVkVSU0lPTiB8fCAnMS4wLjAnKSxcbiAgICAgIF9fQVBQX0VOVl9fOiBKU09OLnN0cmluZ2lmeShtb2RlKVxuICAgIH0sXG5cbiAgICByZXNvbHZlOiB7XG4gICAgICBhbGlhczogW1xuICAgICAgICB7IGZpbmQ6ICdAJywgcmVwbGFjZW1lbnQ6IGZpbGVVUkxUb1BhdGgobmV3IFVSTCgnLi9zcmMnLCBpbXBvcnQubWV0YS51cmwpKSB9LFxuICAgICAgICB7IGZpbmQ6IC9efiguKykvLCByZXBsYWNlbWVudDogZmlsZVVSTFRvUGF0aChuZXcgVVJMKCcuL25vZGVfbW9kdWxlcy8kMScsIGltcG9ydC5tZXRhLnVybCkpIH0sXG4gICAgICAgIHsgZmluZDogJ3Z1ZScsIHJlcGxhY2VtZW50OiAndnVlL2Rpc3QvdnVlLmVzbS1idW5kbGVyLmpzJyB9LFxuICAgICAgICB7IGZpbmQ6ICdAYXNzZXRzJywgcmVwbGFjZW1lbnQ6IGZpbGVVUkxUb1BhdGgobmV3IFVSTCgnLi9zcmMvYXNzZXRzJywgaW1wb3J0Lm1ldGEudXJsKSkgfSxcbiAgICAgICAgeyBmaW5kOiAnQGNvbXBvbmVudHMnLCByZXBsYWNlbWVudDogZmlsZVVSTFRvUGF0aChuZXcgVVJMKCcuL3NyYy9jb21wb25lbnRzJywgaW1wb3J0Lm1ldGEudXJsKSkgfSxcbiAgICAgICAgeyBmaW5kOiAnQHZpZXdzJywgcmVwbGFjZW1lbnQ6IGZpbGVVUkxUb1BhdGgobmV3IFVSTCgnLi9zcmMvdmlld3MnLCBpbXBvcnQubWV0YS51cmwpKSB9LFxuICAgICAgICB7IGZpbmQ6ICdAc3RvcmVzJywgcmVwbGFjZW1lbnQ6IGZpbGVVUkxUb1BhdGgobmV3IFVSTCgnLi9zcmMvc3RvcmVzJywgaW1wb3J0Lm1ldGEudXJsKSkgfSxcbiAgICAgICAgeyBmaW5kOiAnQHV0aWxzJywgcmVwbGFjZW1lbnQ6IGZpbGVVUkxUb1BhdGgobmV3IFVSTCgnLi9zcmMvdXRpbHMnLCBpbXBvcnQubWV0YS51cmwpKSB9LFxuICAgICAgICB7IGZpbmQ6ICdAYXBpJywgcmVwbGFjZW1lbnQ6IGZpbGVVUkxUb1BhdGgobmV3IFVSTCgnLi9zcmMvYXBpJywgaW1wb3J0Lm1ldGEudXJsKSkgfSxcbiAgICAgICAgeyBmaW5kOiAnQHJvdXRlcicsIHJlcGxhY2VtZW50OiBmaWxlVVJMVG9QYXRoKG5ldyBVUkwoJy4vc3JjL3JvdXRlcicsIGltcG9ydC5tZXRhLnVybCkpIH1cbiAgICAgIF0sXG4gICAgICBleHRlbnNpb25zOiBbJy5tanMnLCAnLmpzJywgJy50cycsICcuanN4JywgJy50c3gnLCAnLmpzb24nLCAnLnZ1ZSddXG4gICAgfSxcblxuICAgIHBsdWdpbnM6IFtcbiAgICAgIHZ1ZSh7XG4gICAgICAgIHNjcmlwdDogeyBkZWZpbmVNb2RlbDogdHJ1ZSwgcHJvcHNEZXN0cnVjdHVyZTogdHJ1ZSB9XG4gICAgICB9KVxuICAgIF0sXG5cbiAgICBzZXJ2ZXI6IHtcbiAgICAgIGhvc3Q6ICcwLjAuMC4wJyxcbiAgICAgIHBvcnQ6IDMwMDAsXG4gICAgICBzdHJpY3RQb3J0OiB0cnVlLFxuICAgICAgb3BlbjogdHJ1ZSxcbiAgICAgIGhlYWRlcnM6IHtcbiAgICAgICAgJ0NvbnRlbnQtU2VjdXJpdHktUG9saWN5JzpcbiAgICAgICAgICBcImRlZmF1bHQtc3JjICdzZWxmJzsgXCIgK1xuICAgICAgICAgIFwic2NyaXB0LXNyYyAnc2VsZicgJ3Vuc2FmZS1pbmxpbmUnICd1bnNhZmUtZXZhbCcgaHR0cHM6OyBcIiArXG4gICAgICAgICAgXCJzdHlsZS1zcmMgJ3NlbGYnICd1bnNhZmUtaW5saW5lJyBodHRwczo7IFwiICtcbiAgICAgICAgICBcImZvbnQtc3JjICdzZWxmJyBodHRwczogZGF0YTo7IFwiICtcbiAgICAgICAgICAvLyBcdTI3MDUgQWxsb3cgVW5zcGxhc2ggYW5kIGV4dGVybmFsIENETiBpbWFnZXNcbiAgICAgICAgICBcImltZy1zcmMgJ3NlbGYnIGh0dHBzOi8vaW1hZ2VzLnVuc3BsYXNoLmNvbSBodHRwczogZGF0YTogYmxvYjo7IFwiICtcbiAgICAgICAgICBcImNvbm5lY3Qtc3JjICdzZWxmJyBodHRwczogd3M6IHdzczo7XCJcbiAgICAgIH0sXG4gICAgICBwcm94eToge1xuICAgICAgICAnL2FwaSc6IHtcbiAgICAgICAgICB0YXJnZXQ6ICdodHRwOi8vbG9jYWxob3N0OjgwMDAnLFxuICAgICAgICAgIGNoYW5nZU9yaWdpbjogdHJ1ZSxcbiAgICAgICAgICBzZWN1cmU6IGZhbHNlLFxuICAgICAgICAgIHdzOiB0cnVlLFxuICAgICAgICAgIHJld3JpdGU6IChwYXRoKSA9PiBwYXRoLnJlcGxhY2UoL15cXC9hcGkvLCAnJylcbiAgICAgICAgfSxcbiAgICAgICAgJy9hdXRoJzoge1xuICAgICAgICAgIHRhcmdldDogJ2h0dHA6Ly9sb2NhbGhvc3Q6ODAwMCcsXG4gICAgICAgICAgY2hhbmdlT3JpZ2luOiB0cnVlLFxuICAgICAgICAgIHNlY3VyZTogZmFsc2VcbiAgICAgICAgfVxuICAgICAgfVxuICAgIH0sXG5cbiAgICBidWlsZDoge1xuICAgICAgb3V0RGlyOiAnZGlzdCcsXG4gICAgICBhc3NldHNEaXI6ICdhc3NldHMnLFxuICAgICAgc291cmNlbWFwOiB0cnVlLFxuICAgICAgbWluaWZ5OiAndGVyc2VyJyxcbiAgICAgIHRlcnNlck9wdGlvbnM6IHtcbiAgICAgICAgY29tcHJlc3M6IHtcbiAgICAgICAgICBkcm9wX2NvbnNvbGU6IG1vZGUgPT09ICdwcm9kdWN0aW9uJyxcbiAgICAgICAgICBkcm9wX2RlYnVnZ2VyOiBtb2RlID09PSAncHJvZHVjdGlvbidcbiAgICAgICAgfVxuICAgICAgfSxcbiAgICAgIHJvbGx1cE9wdGlvbnM6IHtcbiAgICAgICAgb3V0cHV0OiB7XG4gICAgICAgICAgbWFudWFsQ2h1bmtzOiB7XG4gICAgICAgICAgICB2dWU6IFsndnVlJywgJ3Z1ZS1yb3V0ZXInLCAncGluaWEnXSxcbiAgICAgICAgICAgIHByaW1ldnVlOiBbJ3ByaW1ldnVlJ10sXG4gICAgICAgICAgICBwcmltZWljb25zOiBbJ3ByaW1laWNvbnMnXSxcbiAgICAgICAgICAgIHByaW1lZmxleDogWydwcmltZWZsZXgnXVxuICAgICAgICAgIH1cbiAgICAgICAgfVxuICAgICAgfVxuICAgIH0sXG5cbiAgICBvcHRpbWl6ZURlcHM6IHtcbiAgICAgIGluY2x1ZGU6IFtcbiAgICAgICAgJ3Z1ZScsXG4gICAgICAgICd2dWUtcm91dGVyJyxcbiAgICAgICAgJ3BpbmlhJyxcbiAgICAgICAgJ3ByaW1ldnVlL2NvbmZpZycsXG4gICAgICAgICdwcmltZXZ1ZS9idXR0b24nLFxuICAgICAgICAncHJpbWV2dWUvaW5wdXR0ZXh0JyxcbiAgICAgICAgJ3ByaW1ldnVlL21lbnUnLFxuICAgICAgICAncHJpbWV2dWUvc2lkZWJhcicsXG4gICAgICAgICdwcmltZXZ1ZS9pbnB1dHN3aXRjaCcsXG4gICAgICAgICdwcmltZWljb25zL3ByaW1laWNvbnMuY3NzJyxcbiAgICAgICAgJ3ByaW1lZmxleC9wcmltZWZsZXguY3NzJ1xuICAgICAgXVxuICAgIH0sXG5cbiAgICBzc3I6IHtcbiAgICAgIG5vRXh0ZXJuYWw6IFsncHJpbWV2dWUnXVxuICAgIH1cbiAgfVxufSlcbiJdLAogICJtYXBwaW5ncyI6ICI7QUFBa1MsU0FBUyxjQUFjLGVBQStCO0FBQ3hWLE9BQU8sU0FBUztBQUNoQixTQUFTLGVBQWUsV0FBVztBQUY4SSxJQUFNLDJDQUEyQztBQUdsTyxJQUFPLHNCQUFRLGFBQWEsQ0FBQyxFQUFFLEtBQUssTUFBaUI7QUFDbkQsUUFBTSxNQUFNLFFBQVEsTUFBTSxRQUFRLElBQUksR0FBRyxFQUFFO0FBRTNDLFNBQU87QUFBQSxJQUNMLEtBQUs7QUFBQSxNQUNILHFCQUFxQjtBQUFBLFFBQ25CLE1BQU07QUFBQSxVQUNKLGdCQUFnQjtBQUFBO0FBQUE7QUFBQTtBQUFBLFFBSWxCO0FBQUEsTUFDRjtBQUFBLElB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
