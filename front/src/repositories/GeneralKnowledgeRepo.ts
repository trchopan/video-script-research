import type {AxiosInstance} from 'axios';

export class _GeneralKnowledgeRepo {
    constructor(private api: AxiosInstance) {}

    async wikipediaSearch(search: string) {
        const {data} = await this.api.post('/general_knowledge_wikipedia_search', {
            search,
        });
        return data.search_results as string[];
    }

    async wikipediaPage(search: string) {
        const {data} = await this.api.post('/general_knowledge_wikipedia_page', {
            search,
        });
        return data.page as string;
    }

    async wikipediaSummary(search: string) {
        const {data} = await this.api.post('/general_knowledge_wikipedia_summary', {
            search,
        });
        return data.summary as string;
    }
}
