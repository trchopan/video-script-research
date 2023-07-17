import axios from 'axios';
import {_YoutubeRepo} from './YoutubeRepo';
import {_AssistantRepo} from './AssistantRepo';
import {_GeneralKnowledgeRepo} from './GeneralKnowledgeRepo';
import {_AppStateRepo} from './AppStateRepo';
import {_SpeechRepo} from './SpeechRepo';

const apiClient = axios.create({
    baseURL: '/api',
    timeout: 3 * 60 * 1000,
});

export const AppStateRepo = new _AppStateRepo(apiClient);
export const YoutubeRepo = new _YoutubeRepo(apiClient);
export const AssistantRepo = new _AssistantRepo(apiClient);
export const GeneralKnowledgeRepo = new _GeneralKnowledgeRepo(apiClient);
export const SpeechRepo = new _SpeechRepo(apiClient);
