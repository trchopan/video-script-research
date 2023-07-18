<script lang="ts">
    import {content, contexts, mediaRecorderSvc} from '@/store';
    import Loading from './Loading.svelte';
    import {AssistantRepo, SpeechRepo} from '@/repositories/inject';

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

    let isRecording = false;
    let stopRecording: () => Promise<Blob[]>;

    const onRecord = async () => {
        isRecording = true;
        stopRecording = await mediaRecorderSvc.startRecord();
    };

    let audioRef: any;
    const onStopRecord = async () => {
        isRecording = false;
        if (!stopRecording) return;
        const chunks = await stopRecording();
        const blob = new Blob(chunks, {type: 'audio/ogg; codecs=opus'});
        const audioURL = window.URL.createObjectURL(blob);
        audioRef.src = audioURL;
        console.log('>>src', audioRef.src);
        const transcriptResp = await SpeechRepo.transcript(blob);
        content.set($content + '\n---\n' + transcriptResp);
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
            {#if !isRecording}
                <button
                    type="button"
                    class="btn variant-ringed-primary btn-sm"
                    on:click={() => onRecord()}
                >
                    Record
                </button>
                {#if audioRef?.src.length > 0}
                    <button
                        type="button"
                        class="btn-icon btn-icon-sm"
                        on:click={() => audioRef.play()}
                    >
                        <span class="text-sm material-icons">play_circle_filled</span>
                    </button>
                {/if}
            {:else}
                <button
                    type="button"
                    class="btn variant-ringed-error btn-sm"
                    on:click={() => onStopRecord()}
                >
                    Stop
                </button>
            {/if}
            <audio bind:this={audioRef} />
        </Loading>
    </div>
</div>
