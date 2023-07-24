import '@skeletonlabs/skeleton/themes/theme-rocket.css';
import '@/theme.scss';
import '@skeletonlabs/skeleton/styles/all.css';
import '@/app.scss';
import '@/plugins/skeleton';
import App from '@/App.svelte';

const app = new App({
    target: document.getElementById('app'),
});

export default app;
