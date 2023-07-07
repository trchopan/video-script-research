<script lang="ts">
    export let loading: boolean;
</script>

{#if loading}
    <span>Loading...</span>
{:else}
    <slot />
{/if}
