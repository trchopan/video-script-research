<script lang="ts">
    import {marked} from 'marked';
    import {onMount} from 'svelte';

    export let content: string;

    $: localContent = marked.parse(content);

    onMount(() => {
        // @ts-ignore
        Prism.highlightAll();
    });
</script>

<div class="text-blue-400 conversation-content">{@html localContent}</div>
