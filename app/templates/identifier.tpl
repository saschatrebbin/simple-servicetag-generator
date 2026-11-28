% include('partials/header.tpl', title='Identifier', lang='de', page_class='identifier')
    <h1>Identifier</h1>
    <ul class="identifier-list">
% for i, item in enumerate(identifiers):
        <li><span class="identifier-value" id="long-{{i}}">{{item['long']}}</span>
            (<span class="identifier-value" id="short-{{i}}">{{item['short']}}</span>)
            <button type="button" onclick="copyValue({{i}}, 'long')">Langform kopieren</button>
            <button type="button" onclick="copyValue({{i}}, 'short')">Kurzform kopieren</button>
            <button type="button" onclick="copyValue({{i}}, 'both')">Beide kopieren</button></li>
% end
    </ul>
    <button type="button" onclick="copyAllIdentifiers()">Alle kopieren</button>
% include('partials/clipboard.tpl')
% include('partials/footer.tpl')
