import {last} from 'lodash';

export enum Tile {
    Transcripts = 'Transcripts',
    Similarity = 'Similarity',
    GeneralKnowledge = 'General Knowledge',
    WriteScript = 'Write Script',
    Conversation = 'Conversation',
    SystemPrompt = 'System Prompt',
    LearnJapanese = 'Learn Japanese',
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

export interface LearnJapaneseExplaination {
    japanese: string;
    romaji: string;
    english: string;
}

export class LearnJapanese {
    japanese: string;
    english: string;
    romaji: string;
    explainations: LearnJapaneseExplaination[];

    static fromApi({japanese, english, romaji, explainations}: any): LearnJapanese {
        return {
            japanese,
            english,
            romaji,
            explainations: explainations
                .map((e: string) => {
                    const matches = e.match(/(.*) \[(.*)\] \[(.*)\]/);
                    if (!matches) return null;
                    return {
                        text: e,
                        japanese: matches[1],
                        romaji: matches[2],
                        english: matches[3],
                    };
                })
                .filter(Boolean),
        };
    }
}

export class YoutubeTranscript {
    chunk: number;
    start: number;
    text: string;
    learn_japanese: LearnJapanese[];

    static fromApi({chunk, start, text, learn_japanese}: any): YoutubeTranscript {
        const o = new YoutubeTranscript();
        o.chunk = chunk;
        o.start = start;
        o.text = text;
        o.learn_japanese = (learn_japanese ? JSON.parse(learn_japanese) : []).map(
            LearnJapanese.fromApi
        );
        return o;
    }
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
    Youtube = 'youtube',
}

export interface ConversationChatToolData {
    data?: object;
}

export type ConversationChatToolsRecord = Partial<
    Record<ConversationChatToolEnum, ConversationChatToolData>
>;

export interface SystemPrompt {
    _id: number;
    name: string;
    template: string;
    timestamp: string;
}
