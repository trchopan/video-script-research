<script lang="ts">
    import {content, contexts} from '@/store';
    import Loading from './Loading.svelte';
    import {AssistantRepo} from '@/repositories/inject';

    let loading = false;
    const partialTool = async (fn: () => Promise<string>) => {
        try {
            loading = true;
            const info = await fn();
            content.set($content + '\n---\n' + info);
        } finally {
            loading = false;
        }
    };

    const onExtendContent = async () => {
        partialTool(() => AssistantRepo.extendWithContext($content, $contexts));
    };

    const onTranslateContent = async () => {
        partialTool(() => AssistantRepo.translateText($content, 'Vietnamese'));
    };

    const onChat = async () => {
        partialTool(() => AssistantRepo.chat($content));
    };
</script>

<div>
    <textarea
        bind:value={$content}
        class="textarea leading-7 h-[90vh]"
        placeholder="Enter Content"
    />
    <div class="flex gap-3">
        <Loading {loading}>
            <button
                type="button"
                class="btn variant-filled-primary btn-sm"
                on:click={() => onExtendContent()}
            >
                Extend
            </button>
            <button
                type="button"
                class="btn variant-ringed-primary btn-sm"
                on:click={() => onTranslateContent()}
            >
                Translate
            </button>
            <button
                type="button"
                class="btn variant-ringed-primary btn-sm"
                on:click={() => onChat()}
            >
                Chat
            </button>
        </Loading>
    </div>
</div>
