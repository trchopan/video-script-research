<script lang="ts">
    import {getSelectionText} from '@/helpers';
    import {contexts, playYtPlayer} from '@/store';

    export let chunk: {video_id: string; chunk: number; text: string; start: number};

    const onPlayYtVideo = (video_id: string, start: number) => {
        playYtPlayer(video_id, start);
    };

    const onAddTranscript = (text: string) => {
        const _text = getSelectionText() || text;
        contexts.set($contexts.concat(_text));
    };

    // Convert the seconds into duration format `<minutes>m<seconds>s`
    const secondToDuration = (seconds: number) => {
        const _minutes = Math.floor(seconds / 60);
        const _seconds = seconds % 60;
        return (_minutes > 0 ? `${_minutes.toFixed(0)}m` : '') + `${_seconds.toFixed(0)}s`;
    };
</script>

<div class="flex items-center place-content-between py-3 px-3">
    <div class="text-stone-400 text-xs py-2">
        <span>Chunk: {chunk.chunk} | Time: {secondToDuration(chunk.start)}</span>
        <slot />
    </div>

    <div class="flex gap-3">
        <button
            type="button"
            class="btn-icon btn-icon-sm variant-filled"
            on:click={() => onPlayYtVideo(chunk.video_id, chunk.start)}
        >
            <span class="text-sm material-icons">play_arrow</span>
        </button>
        <button
            type="button"
            class="btn-icon btn-icon-sm variant-filled"
            on:click={() => onAddTranscript(chunk.text)}
        >
            <span class="text-sm material-icons">add</span>
        </button>
    </div>
</div>
