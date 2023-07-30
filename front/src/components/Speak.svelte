<script lang="ts">
    import {SpeechRepo} from '@/repositories/inject';
    import {mediaRecorderSvc} from '@/store';

    let isRecording = false;
    let stopRecording: () => Promise<Blob[]>;

    const onSpeak = async () => {
        isRecording = true;
        stopRecording = await mediaRecorderSvc.startRecord();
    };

    let audioRef: any;
    export let transcriptCb: (transcript: string) => void;
    export const onStopRecord = async () => {
        isRecording = false;
        if (!stopRecording) return;
        const chunks = await stopRecording();
        const blob = new Blob(chunks, {type: 'audio/ogg; codecs=opus'});
        const audioURL = window.URL.createObjectURL(blob);
        audioRef.src = audioURL;
        console.log('>>src', audioRef.src);
        const transcriptResp = await SpeechRepo.transcript(blob);
        transcriptCb(transcriptResp);
    };
</script>

<div class="flex gap-3">
    {#if !isRecording}
        <button type="button" class="btn variant-ringed-primary btn-sm" on:click={() => onSpeak()}>
            Speak
        </button>
        {#if audioRef?.src.length > 0}
            <a href={audioRef.src} target="_blank" class="btn-icon btn-icon-sm">
                <span class="text-sm material-icons">play_circle_filled</span>
            </a>
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
</div>
