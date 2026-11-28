<!DOCTYPE html>
<html lang="{{lang}}">
<head>
    <meta charset="UTF-8">
    <title>{{title}}</title>
    <style>
        body { font-family: Arial, sans-serif; color: #333; }
        .nanoid, .password-page { text-align: center; margin-top: 50px; }
        .identifier { margin: 3em auto; max-width: 70em; padding: 0 1em; }
        .nanoid h1 { margin-bottom: 0.25em; }
        .meta { font-size: 0.85em; color: #888; margin-bottom: 1.5em; }
        .id-value, .identifier-value, .password { white-space: pre-wrap; }
        .id-value, .identifier-value { font-family: monospace; }
        .id-value { font-size: 1.2em; }
        .id-list { list-style: none; padding: 0; display: inline-block; text-align: left; }
        .id-list li { display: flex; align-items: center; gap: 0.75em;
                      padding: 0.4em 0.6em; border-bottom: 1px solid #eee; }
        .id-list li:last-child { border-bottom: none; }
        .identifier li { padding: .7em 0; }
        button { cursor: pointer; }
        .identifier button { margin: .2em; }
        .copy-btn { padding: 0.25em 0.75em; font-size: 0.8em; border: 1px solid #aaa;
                    border-radius: 4px; background: #f5f5f5; }
        .copy-btn:hover { background: #e0e0e0; }
        .copy-all { font-size: 1em; margin-top: 1.2em; padding: 0.4em 1.2em; }
        .single-box { font-size: 1.5em; padding: 20px 32px; background: #f5f5f5;
                      display: inline-block; border-radius: 6px; margin-bottom: 1em; }
        .password { font-size: 24px; padding: 20px; background: #f5f5f5;
                    display: inline-block; border-radius: 5px; }
    </style>
</head>
<body class="{{page_class}}">
