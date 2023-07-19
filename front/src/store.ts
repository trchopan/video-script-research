import {get, writable, type Writable} from 'svelte/store';
import {
    type YoutubeVideo,
    type YoutubeSimilarity,
    type YoutubeTranscript,
    Tile,
} from '@/repositories/types';
import {AppStateRepo, YoutubeRepo} from './repositories/inject';
import {debounce, isEmpty} from 'lodash';
import { MediaRecorderService } from './services/mediaRecorder';

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

export const searchResult = writable('');
export const multipleSearchResults = writable<string[]>([]);

export const researchVideoIds = writable<string[]>([]);
export const contexts = writable<string[]>([]);
export const content = writable('');

type StringOrStringArray = string | string[];
interface LoadList {
    [key: string]: {val: Writable<StringOrStringArray>; default: StringOrStringArray};
}
const loadList: LoadList = {
    researchVideoIds: {val: researchVideoIds, default: []},
    content: {val: content, default: ''},
    contexts: {val: contexts, default: []},
};

export const currentAppId = writable<string>(window.localStorage.getItem('app_id') || '');

export const saveAppState = () => {
    const app_id = get(currentAppId);
    if (!app_id) return;
    const newData = Object.entries(loadList).reduce(
        (acc, [k, v]) => {
            acc[k] = get(v.val);
            return acc;
        },
        {} as {[key: string]: StringOrStringArray}
    );
    AppStateRepo.saveData(app_id, newData);
};

export const loadAppState = async () => {
    const app_id = window.localStorage.getItem('app_id');
    if (!app_id) return;

    const appState = await AppStateRepo.get(app_id);

    for (const [key, value] of Object.entries(loadList)) {
        try {
            const data = appState.data[key];
            if (!isEmpty(data)) {
                value.val.set(data);
            } else {
                value.val.set(value.default);
            }
        } catch {
            console.log('>>> not saved', key);
        }
    }
};

const debouncedSaveAppState = debounce(() => saveAppState(), 5 * 1000);
const initAppState = async () => {
    await loadAppState();
    Object.values(loadList).map(value =>
        value.val.subscribe(() => {
            debouncedSaveAppState();
        })
    );
};
initAppState();

currentAppId.subscribe(app_id => {
    window.localStorage.setItem('app_id', app_id);
    loadAppState();
});

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
export const playYtPlayer = (video_id: string, start: number) => {
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

export const mediaRecorderSvc = new MediaRecorderService();
