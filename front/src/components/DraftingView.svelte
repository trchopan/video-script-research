<script lang="ts">
    import {content, contexts, mediaRecorder} from '@/store';
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

    let chunks = [];
    let isRecording = false;

    const onRecord = async () => {
        if (!$mediaRecorder) return;
        isRecording = true;
        $mediaRecorder.start();
        console.log($mediaRecorder.state);
        console.log('recorder started');
        $mediaRecorder.ondataavailable = e => {
            chunks.push(e.data);
        };
    };

    let audioRef;
    const onStopRecord = async () => {
        //
        isRecording = false;
        $mediaRecorder.stop();
        $mediaRecorder.onstop = async e => {
            console.log($mediaRecorder.state);
            console.log('recorder stopped');
            console.log('>>>', chunks);
            const blob = new Blob(chunks, {type: 'audio/ogg; codecs=opus'});
            const audioURL = window.URL.createObjectURL(blob);
            audioRef.src = audioURL;
            const transcriptResp = await SpeechRepo.transcript(blob);
            content.set($content + '\n---\n' + transcriptResp);
            chunks = [];
        };
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
            <audio bind:this={audioRef} />
            {#if !isRecording}
                <button
                    type="button"
                    class="btn variant-ringed-primary btn-sm"
                    on:click={() => onRecord()}
                >
                    Record
                </button>
            {:else}
                <button
                    type="button"
                    class="btn variant-ringed-error btn-sm"
                    on:click={() => onStopRecord()}
                >
                    Stop
                </button>
            {/if}
        </Loading>
    </div>
</div>
