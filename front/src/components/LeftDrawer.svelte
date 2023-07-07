<script lang="ts">
    import {Drawer} from '@skeletonlabs/skeleton';
    import {
        getNewVideoTranscript,
        loadingNewVideoTranscript,
        researchVideoIds,
        videos,
    } from '@/store';
    import Loading from './Loading.svelte';

    let youtubeUrl: string = '';

    const onToggleResearchVideoIds = (video_id: string) => {
        if ($researchVideoIds.includes(video_id)) {
            researchVideoIds.set($researchVideoIds.filter(v => v != video_id));
        } else {
            researchVideoIds.set($researchVideoIds.concat(video_id));
        }
    };

    const onAddNewVideoTranscript = () => {
        getNewVideoTranscript(youtubeUrl);
        youtubeUrl = '';
    };
</script>

<Drawer id="left-drawer" width="w-[600px]">
    <div>
        <Loading loading={$loadingNewVideoTranscript}>
            <div class="flex gap-5 items-center">
                <input bind:value={youtubeUrl} class="input" type="text" placeholder="Input" />
                <button
                    on:click={() => onAddNewVideoTranscript()}
                    class="btn variant-ringed-secondary"
                >
                    Add
                </button>
            </div>
        </Loading>
        <ul class="list max-h-[10rem]">
            {#each $videos as video}
                <!-- svelte-ignore a11y-click-events-have-key-events -->
                <li
                    on:click={() => onToggleResearchVideoIds(video.video_id)}
                    class:selected={$researchVideoIds.includes(video.video_id)}
                    class="pr-3"
                >
                    <div class="w-32 h-20 flex items-center pl-3">
                        <img src={video.thumbnail} class="object-cover" alt={video.title} />
                    </div>
                    <div class="w-full">
                        <span class="flex-auto">{video.title}</span>
                    </div>
                </li>
            {/each}
        </ul>
    </div>
</Drawer>

<style>
    .selected {
        @apply text-red-400;
    }
</style>
