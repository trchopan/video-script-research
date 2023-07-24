import {cloneDeep} from 'lodash';

export function textAreaAdjust(element: any) {
    element.target.style.height = '1px';
    element.target.style.height = element.target.scrollHeight + 'px';
}

export function getSelectionText() {
    var text = '';
    if (window.getSelection) {
        text = window.getSelection().toString();
    } else if ((document as any).selection && (document as any).selection.type != 'Control') {
        text = (document as any).selection.createRange().text;
    }
    return text;
}
