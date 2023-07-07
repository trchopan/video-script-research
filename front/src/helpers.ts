export function textAreaAdjust(element: any) {
    element.target.style.height = '1px';
    element.target.style.height = element.target.scrollHeight + 'px';
}
