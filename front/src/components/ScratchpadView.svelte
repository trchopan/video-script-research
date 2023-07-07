<script lang="ts">
    import {AssistantRepo} from '@/repositories/inject';
    import {contexts} from '@/store';
    import {cloneDeep} from 'lodash';
    import Loading from './Loading.svelte';

    const onAddContext = () => {
        contexts.set($contexts.concat(''));
    };

    const onRemoveContext = (i: number) => {
        let cloneContext = cloneDeep($contexts);
        cloneContext.splice(i, 1);
        contexts.set(cloneContext);
    };

    let loading: {[key: number]: boolean} = {};
    const partialTool = async (i: number, fn: () => Promise<string>) => {
        try {
            loading[i] = true;
            const info = await fn();
            let cloneContext = cloneDeep($contexts);
            cloneContext.splice(i, 1, cloneContext[i] + '\n---\n' + info);
            contexts.set(cloneContext);
        } finally {
            loading[i] = false;
        }
    };
    const onExtract = async (i: number) => {
        partialTool(i, () => AssistantRepo.extractInformation($contexts[i]));
    };

    const onFormat = async (i: number) => {
        partialTool(i, () => AssistantRepo.formatText($contexts[i]));
    };
</script>

<h4 class="text-orange-400">Scratch Pad</h4>
<div class="flex flex-col gap-3 max-h-[85vh] overflow-y-scroll">
    <div class="h-full flex flex-col gap-3">
        {#each $contexts as ctx, i}
            <div>
                <textarea bind:value={ctx} class="textarea leading-7" rows="6" />
                <div class="flex gap-3">
                    <button
                        type="button"
                        class="btn variant-ringed-secondary btn-sm"
                        on:click={() => onRemoveContext(i)}
                    >
                        Remove
                    </button>
                    <Loading loading={loading[i]}>
                        <button
                            type="button"
                            class="btn variant-ringed-secondary btn-sm"
                            on:click={() => onExtract(i)}
                        >
                            Extract
                        </button>
                        <button
                            type="button"
                            class="btn variant-ringed-secondary btn-sm"
                            on:click={() => onFormat(i)}
                        >
                            Format
                        </button>
                    </Loading>
                </div>
            </div>
        {/each}
    </div>
    <div>
        <button on:click={() => onAddContext()} class="btn variant-ringed-primary" type="button">
            Add
        </button>
    </div>
</div>
