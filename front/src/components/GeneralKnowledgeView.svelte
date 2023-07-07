<script lang="ts">
    import {
        contexts,
        getWikipediaPage,
        loadingWikipediaSearch,
        wikipediaSearchResult,
        wikipediaSearchString,
    } from '@/store';
    import TextToParagraph from './TextToParagraph.svelte';
    import HalfPageWithLoading from './HalfPageWithLoading.svelte';

    const onAddTranscript = (text: string) => {
        contexts.set($contexts.concat(text));
    };

    const onSearchWikipediaPage = async () => {
        getWikipediaPage();
    };

    const onSearchWikipediaSummary = async () => {
        getWikipediaPage({summary: true});
    };
</script>

<div class="flex flex-col gap-5">
    <div class="flex gap-5">
        <input bind:value={$wikipediaSearchString} class="input" type="text" placeholder="Input" />
        <button
            on:click={() => onSearchWikipediaPage()}
            class="btn variant-ringed-secondary"
            disabled={$loadingWikipediaSearch}
        >
            Page
        </button>
        <button
            on:click={() => onSearchWikipediaSummary()}
            class="btn variant-ringed-secondary"
            disabled={$loadingWikipediaSearch}
        >
            Summary
        </button>
    </div>
    <HalfPageWithLoading loading={$loadingWikipediaSearch}>
        <div class="flex justify-end">
            <button
                type="button"
                class="btn-icon btn-icon-sm variant-filled"
                on:click={() => onAddTranscript($wikipediaSearchResult)}
            >
                <span class="text-sm material-icons">add</span>
            </button>
        </div>
        <TextToParagraph text={$wikipediaSearchResult} />
    </HalfPageWithLoading>
</div>
