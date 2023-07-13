import {defineConfig} from 'vite';
import {svelte} from '@sveltejs/vite-plugin-svelte';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [svelte()],
    resolve: {
        alias: {
            '@': path.resolve(__dirname, './src'),
        },
    },
    server: {
        port: 6968,
        proxy: {
            '/api': {
                target: 'http://127.0.0.1:6969',
                rewrite: path => path.replace(/^\/api/, ''),
            },
        },
    },
});
