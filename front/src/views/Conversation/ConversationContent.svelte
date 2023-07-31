<script lang="ts">
    import {marked} from 'marked';
    import {onMount} from 'svelte';

    export let content: string;

    $: localContent = marked.parse(content, {
        mangle: false,
        headerIds: false,
    });

    onMount(() => {
        // @ts-ignore
        Prism.highlightAll();
    });
</script>

<div class="conversation-content">{@html localContent}</div>
