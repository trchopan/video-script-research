<script lang="ts">
    export let text: string;
</script>

<div class="flex flex-col gap-5 leading-7">
    {#each text.split('\n').filter(Boolean) as p}
        <p>{p}</p>
    {/each}
</div>
