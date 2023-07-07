import {get, writable} from 'svelte/store';
import {
    type YoutubeVideo,
    type YoutubeSimilarity,
    type YoutubeTranscript,
    Tile,
} from '@/repositories/types';
import {GeneralKnowledgeRepo, YoutubeRepo} from './repositories/inject';

export const openTranscript = writable(false);

export const tileOptions = [Tile.Transcripts, Tile.Similarity, Tile.GeneralKnowledge, Tile.Extend];
export const currentTile = writable<Tile>(Tile.Transcripts);

export const videos = writable<YoutubeVideo[]>([]);
export const loadingVideos = writable<boolean>(false);
export const getVideos = async () => {
    loadingVideos.set(true);
    try {
        videos.set(await YoutubeRepo.getVideos());
    } finally {
        loadingVideos.set(false);
    }
};

export const selectedVideoId = writable('');
export const transcripts = writable<YoutubeTranscript[]>([]);
export const similarityQuery = writable('');
export const similarities = writable<YoutubeSimilarity[]>([]);

export const loadingNewVideoTranscript = writable<boolean>(false);
export const getNewVideoTranscript = async (youtubeUrl: string) => {
    loadingNewVideoTranscript.set(true);
    try {
        await YoutubeRepo.getVideoTranscript(YoutubeRepo.parseYoutubeVideoId(youtubeUrl), true);
        await getVideos();
    } finally {
        loadingNewVideoTranscript.set(false);
    }
};

export const wikipediaSearchString = writable('');
export const wikipediaSearchResult = writable('');
export const loadingWikipediaSearch = writable<boolean>(false);
export const getWikipediaPage = async (opt: {summary: boolean} = {summary: false}) => {
    loadingWikipediaSearch.set(true);
    try {
        const searchString = get(wikipediaSearchString);
        const page = opt.summary
            ? await GeneralKnowledgeRepo.wikipediaSummary(searchString)
            : await GeneralKnowledgeRepo.wikipediaPage(searchString);
        wikipediaSearchResult.set(page);
    } finally {
        loadingWikipediaSearch.set(false);
    }
};

export const researchVideoIds = writable<string[]>([]);
export const contexts = writable<string[]>([]);
export const content = writable('');

const loadList = [
    {val: researchVideoIds, key: 'researchVideoIds'},
    {val: wikipediaSearchString, key: 'wikipediaSearchString'},
    {val: wikipediaSearchResult, key: 'wikipediaSearchResult'},
    {val: content, key: 'content'},
    {val: contexts, key: 'contexts'},
];

let loaded = false;

export const loadLocalStorage = () => {
    if (loaded) return;

    for (const toLoad of loadList) {
        try {
            const savedContent = JSON.parse(window.localStorage.getItem(toLoad.key) || '');
            toLoad.val.set(savedContent);
        } catch {
            console.log('>>> not saved', toLoad.key);
        }
        toLoad.val.subscribe((v: any) => {
            console.log('>>>', toLoad.key, v);
            window.localStorage.setItem(toLoad.key, JSON.stringify(v));
        });
    }

    loaded = true;
};

export const ytVideoShow = writable(false);
export const ytReady = writable(false);
let ytPlayer = null;
export const initYtPlayer = () => {
    ytPlayer =
        // @ts-ignore
        new YT.Player('yt-player', {
            height: '390',
            width: '640',
            playerVars: {
                playsinline: 1,
            },
        });
    // For debug
    // (window as any).ytPlayer = ytPlayer
};
export const loadYtPlayer = (video_id: string, start: number) => {
    if (ytPlayer.getVideoData().video_id === video_id) {
        ytPlayer.seekTo(start);
    } else {
        ytPlayer.loadVideoById({videoId: video_id, startSeconds: start});
    }
    ytVideoShow.set(true);
};

export const showYtPlayer = () => {
    ytVideoShow.set(true);
};
export const hideYtPlayer = () => {
    ytPlayer.pauseVideo();
    ytVideoShow.set(false);
};
