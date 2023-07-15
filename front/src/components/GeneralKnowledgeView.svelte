<script lang="ts">
    import {contexts, multipleSearchResults, searchResult} from '@/store';
    import TextToParagraph from './TextToParagraph.svelte';
    import {GeneralKnowledgeRepo} from '@/repositories/inject';
    import Loading from './Loading.svelte';
    import {getSelectionText} from '@/helpers';

    let loading = false;
    let search = '';

    const onAddTranscript = (text: string) => {
        const _text = getSelectionText() || text;
        contexts.set($contexts.concat(_text));
    };

    const onSearchWikipediaPage = async () => {
        loading = true;
        multipleSearchResults.set(await GeneralKnowledgeRepo.wikipediaSearch(search));
        searchResult.set('');
        loading = false;
    };

    const onGetPage = async (page: string) => {
        loading = true;
        searchResult.set(await GeneralKnowledgeRepo.wikipediaPage(page));
        loading = false;
    };

    const onGetSummary = async (page: string) => {
        loading = true;
        searchResult.set(await GeneralKnowledgeRepo.wikipediaSummary(page));
        loading = false;
    };
</script>

<div class="flex flex-col gap-5">
    <form class="flex gap-5" on:submit|preventDefault={() => onSearchWikipediaPage()}>
        <input bind:value={search} class="input" type="text" placeholder="Input" />
        <Loading {loading}>
            <button class="btn variant-ringed-primary" type="submit">Search</button>
        </Loading>
    </form>
    <ul class="list h-[20vh] overflow-y-scroll">
        {#each $multipleSearchResults as result}
            <!-- svelte-ignore a11y-click-events-have-key-events -->
            <li class="flex place-content-between">
                <div class="flex gap-3 items-center">
                    <div class="w-full">
                        <span class="flex-auto">{result}</span>
                    </div>
                </div>
                <div>
                    <button
                        type="button"
                        class="btn variant-ringed-secondary btn-sm"
                        on:click={() => onGetSummary(result)}
                    >
                        Summary
                    </button>
                    <button
                        type="button"
                        class="btn variant-ringed-secondary btn-sm"
                        on:click={() => onGetPage(result)}
                    >
                        Page
                    </button>
                </div>
            </li>
        {/each}
    </ul>

    <hr />

    {#if $searchResult.length > 0}
        <div class="flex justify-end">
            <button
                type="button"
                class="btn-icon btn-icon-sm variant-filled"
                on:click={() => onAddTranscript($searchResult)}
            >
                <span class="text-sm material-icons">add</span>
            </button>
        </div>

        <div class="h-[70vh] overflow-y-scroll">
            <Loading {loading}>
                <TextToParagraph text={$searchResult} />
            </Loading>
        </div>
    {/if}
</div>
