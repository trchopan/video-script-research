export enum Tile {
    Transcripts = 'Transcripts',
    Similarity = 'Similarity',
    GeneralKnowledge = 'General Knowledge',
    WriteScript = 'Write Script',
    Conversation = 'Conversation',
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

export interface Conversation {
    conversation_id: string;
    name: string;
    timestamp: Date;
    system_prompt: string;
    memory: Memory[];
}

export interface Memory {
    type: string;
    data: MemoryData;
}

export interface MemoryData {
    content: string;
    additional_kwargs: object;
    example: boolean;
}

export enum ConversationChatToolEnum {
    Wikipedia = 'wikipedia',
    DuckduckGo = 'duckduckgo',
}

export interface ConversationChatToolData {
    data?: object;
}

export type ConversationChatToolsRecord = Partial<
    Record<ConversationChatToolEnum, ConversationChatToolData>
>;
