<script lang="ts">
    import type {LearnJapanese, LearnJapaneseExplaination} from '@/repositories/types';
    import {shuffle} from 'lodash';

    export let item: LearnJapanese;

    const makeExplaination = (
        language: string,
        explainationLanguage: ({color: string} & LearnJapaneseExplaination)[]
    ) => {
        const itemLanguage: string = item[language];
        if (!itemLanguage) return '';
        let sentence: string[] = [];
        for (let i = 0; i < itemLanguage.length; i++) {
            sentence.push(itemLanguage[i]);
        }
        let startAfterIndex = 0;
        const explainationWithPosition = explainationLanguage
            .map(e => {
                const position = itemLanguage
                    .toLowerCase()
                    .indexOf(e[language].toLowerCase(), startAfterIndex);
                if (language !== 'english') {
                    startAfterIndex = position;
                }
                return {
                    position,
                    len: e[language].length,
                    ...e,
                };
            })
            .filter(e => e.position >= 0);

        for (const e of explainationWithPosition) {
            sentence[e.position] = `<span class="${e.color}">` + sentence[e.position];
            sentence[e.position + e.len - 1] = sentence[e.position + e.len - 1] + '</span>';
        }
        return sentence.join('');
    };

    const colors = shuffle([
        'text-pink-400',
        'text-orange-400',
        'text-purple-400',
        'text-yellow-400',
        'text-amber-400',
        'text-red-400',
        'text-green-400',
        'text-blue-400',
        'text-teal-400',
        'text-indigo-400',
    ]);

    $: localExplaination = item.explainations.map((e, i) => ({
        color: colors[i % colors.length],
        ...e,
    }));

    $: jaHtml = (function (explainations: ({color: string} & LearnJapaneseExplaination)[]) {
        return makeExplaination('japanese', explainations);
    })(localExplaination);

    $: enHtml = (function (explainations: ({color: string} & LearnJapaneseExplaination)[]) {
        return makeExplaination('english', explainations);
    })(localExplaination);

    $: roHtml = (function (explainations: ({color: string} & LearnJapaneseExplaination)[]) {
        return makeExplaination('romaji', explainations);
    })(localExplaination);
</script>

<div class="grid grid-cols-[2fr,1fr] gap-3">
    <div>
        <div class="text-sm">{@html roHtml}</div>
        <div>{@html jaHtml}</div>
        <div>{@html enHtml}</div>
    </div>
    <div>
        {#each localExplaination as explaination, i}
            <div class={`grid grid-cols-[1fr,1fr,1fr] gap-3 ${explaination.color}`}>
                <span>{explaination.romaji}</span>
                <span>{explaination.japanese}</span>
                <span>{explaination.english}</span>
            </div>
        {/each}
    </div>
</div>
