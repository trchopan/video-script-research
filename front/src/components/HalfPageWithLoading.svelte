<script lang="ts">
    import Loading from '@/components/Loading.svelte';

    export let loading: boolean;
</script>

<Loading {loading}>
    <div class="max-h-[85vh] overflow-y-scroll">
        <div class="flex flex-col gap-3">
            <slot />
        </div>
    </div>
</Loading>
