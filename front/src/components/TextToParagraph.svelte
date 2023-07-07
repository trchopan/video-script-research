<script lang="ts">
    export let text: string;
</script>

<div>
    {#each text.split('\n') as p}
        <p>{p}</p>
    {/each}
</div>
