import type {AxiosInstance} from 'axios';

export class _AssistantRepo {
    constructor(private api: AxiosInstance) {}

    async extendWithContext(content: string, context: string[]) {
        const {data} = await this.api.post('/assistant_writer_extend_with_context', {
            content,
            context,
        });
        return data.extended_content as string;
    }

    async extractInformation(documents: string) {
        const {data} = await this.api.post('/assistant_extract_information', {
            documents,
        });
        return data.scratch_pad as string;
    }

    async translateText(text: string, language: string) {
        const {data} = await this.api.post('/assistant_translate', {
            text,
            language,
        });
        return data.translated as string;
    }

    async formatText(text: string) {
        const {data} = await this.api.post('/assistant_format', {
            text,
        });
        return data.formated as string;
    }

    async chat(chat: string) {
        const {data} = await this.api.post('/assistant_chat', {
            chat,
        });
        return data.response as string;
    }
}
