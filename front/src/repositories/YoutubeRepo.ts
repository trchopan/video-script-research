import type {AxiosInstance} from 'axios';
import type {YoutubeSimilarity, YoutubeTranscript, YoutubeVideo} from './types';

export class _YoutubeRepo {
    constructor(private api: AxiosInstance) {}

    parseYoutubeVideoId(url: string) {
        var regExp = /^.*((youtu.be\/)|(v\/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#&?]*).*/;
        var match = url.match(regExp);
        return match && match[7].length == 11 ? match[7] : undefined;
    }

    async getVideos() {
        const {data} = await this.api.get('/list_youtube_videos');
        return data.videos as YoutubeVideo[];
    }

    async getVideoTranscript(video_id: string, clearCache: boolean = false) {
        const {data} = await this.api.post(
            '/get_youtube_transcript',
            {
                link: `https://www.youtube.com/watch?v=${video_id}`,
            },
            {params: {clear_cache: clearCache ? 1 : undefined}}
        );
        return data.transcripts as YoutubeTranscript[];
    }

    async getSimilarity(query: string, video_ids: string[]) {
        const {data} = await this.api.post('/youtube_transcript_similarity', {
            query,
            links: video_ids.map(video_id => `https://www.youtube.com/watch?v=${video_id}`),
            k: 10,
        });
        return data.similarity as YoutubeSimilarity[];
    }

    async enrichWithContext(content: string, context: string[]) {
        const {data} = await this.api.post('/assistant_writer_enrich_with_context', {
            content,
            context,
        });
        return data.enriched_content as string;
    }

    async extractInfoFromContext(content: string, context: string) {
        const {data} = await this.api.post('/assistant_extract_relevant_information', {
            content,
            context,
        });
        return data.scratch_pad as string;
    }
}
