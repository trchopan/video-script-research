<script lang="ts">
    import {YoutubeRepo} from '@/repositories/inject';
    import {researchVideoIds, similarities, similarityQuery, videos} from '@/store';
    import Loading from './Loading.svelte';
    import ChunkInfo from './ChunkInfo.svelte';
    import TextToParagraph from './TextToParagraph.svelte';
    import HalfPageWithLoading from './HalfPageWithLoading.svelte';

    let loading = false;

    const onQuerySimilarity = async () => {
        loading = true;
        try {
            similarities.set(await YoutubeRepo.getSimilarity($similarityQuery, $researchVideoIds));
        } finally {
            loading = false;
        }
    };

    const findVideo = (video_id: string) => {
        return $videos.find(v => v.video_id === video_id);
    };
</script>

<div class="flex flex-col gap-5">
    <form class="flex gap-5" on:submit|preventDefault={() => onQuerySimilarity()}>
        <input bind:value={$similarityQuery} class="input" type="text" placeholder="Input" />
        <Loading {loading}>
            <button type="submit" class="btn variant-ringed-primary">Query</button>
        </Loading>
    </form>
    <HalfPageWithLoading {loading}>
        {#each $similarities as similarity}
            {@const foundVideo = findVideo(similarity.document)}
            <div>
                <div class="text-red-400">{foundVideo?.title}</div>
                <ChunkInfo
                    chunk={{
                        video_id: foundVideo?.video_id || '',
                        chunk: similarity.chunk,
                        start: similarity.start,
                        text: similarity.content,
                    }}
                >
                    <span>| Score: {similarity.similarity.toFixed(3)}</span>
                </ChunkInfo>
                <div class="leading-7">
                    <TextToParagraph text={similarity.content} />
                </div>
            </div>
            <hr />
        {/each}
    </HalfPageWithLoading>
</div>
