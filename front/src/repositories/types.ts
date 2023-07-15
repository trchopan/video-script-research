export enum Tile {
    Transcripts = 'Transcripts',
    Similarity = 'Similarity',
    GeneralKnowledge = 'General Knowledge',
    Extend = 'Extend',
}

export interface AppState {
    app_id: string;
    data: any;
    name: string;
    timestamp: string;
}

export interface YoutubeVideo {
    video_id: string;
    title: string;
    thumbnail: string;
    channel: string;
    channel_id: string;
    description: string;
    publish_at: Date;
}

export interface YoutubeTranscript {
    chunk: number;
    start: number;
    text: string;
}

export interface YoutubeSimilarity {
    chunk: number;
    content: string;
    document: string;
    namespace: string;
    similarity: number;
    start: number;
}
