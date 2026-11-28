<script>
function copyOne(i) {
    const el = document.getElementById('id-' + i);
    navigator.clipboard.writeText(el.textContent).then(() => {
        el.style.background = '#d4edda';
        setTimeout(() => el.style.background = '', 1000);
    });
}
function copyAllNano() {
    const els = document.querySelectorAll('.id-value');
    const text = Array.from(els).map(el => el.textContent).join('\n');
    navigator.clipboard.writeText(text);
}
function value(i, part) {
    return document.getElementById(part + '-' + i).textContent;
}
function copyValue(i, part) {
    const text = part === 'both' ? value(i, 'long') + ' (' + value(i, 'short') + ')' : value(i, part);
    navigator.clipboard.writeText(text);
}
function copyAllIdentifiers() {
    const items = document.querySelectorAll('.identifier-list li');
    navigator.clipboard.writeText(Array.from(items, (_, i) => value(i, 'long') + ' (' + value(i, 'short') + ')').join('\n'));
}
</script>
