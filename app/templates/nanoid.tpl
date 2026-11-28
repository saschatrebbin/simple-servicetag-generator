% include('partials/header.tpl', title='Nano IDs', lang='de', page_class='nanoid')
    <h1>Nano IDs</h1>
    <p class="meta">
        {{count}} ID{{'s' if count > 1 else ''}} &nbsp;|&nbsp;
        Länge: {{meta['length']}} &nbsp;|&nbsp;
        Alphabet: {{meta['alphabet_size']}} Zeichen &nbsp;|&nbsp;
        Kollisionswahrsch.: {{col_str}}
    </p>
% if count == 1:
    <div class="single-box"><div class="id-value" id="id-0">{{ids[0]}}</div></div>
    <button class="copy-btn" type="button" onclick="copyOne(0)">Kopieren</button>
% else:
    <ul class="id-list">
% for i, item in enumerate(ids):
        <li><span class="id-value" id="id-{{i}}">{{item}}</span>
            <button class="copy-btn" type="button" onclick="copyOne({{i}})">Kopieren</button></li>
% end
    </ul>
    <button class="copy-btn copy-all" type="button" onclick="copyAllNano()">Alle kopieren</button>
% end
% include('partials/clipboard.tpl')
% include('partials/footer.tpl')
