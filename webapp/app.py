import os
import sys
import tempfile

from flask import Flask, request, send_file, render_template_string

# Allow importing from the parent project's lib/ directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from lib.au import concat_au

app = Flask(__name__)
app.config['APPLICATION_ROOT'] = '/cisco-isr-pfm'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIT_DIR  = os.path.join(BASE_DIR, 'sit')
AU_DIR   = os.path.join(BASE_DIR, 'au')

def list_au_files(directory):
    return sorted(
        f for f in os.listdir(directory)
        if f.lower().endswith('.au')
    )

TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Cisco ISR SIT + Message File Generator</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #0f1117;
      color: #e2e8f0;
      min-height: 100vh;
      padding: 2rem 1rem 4rem;
    }

    .container {
      max-width: 680px;
      margin: 0 auto;
    }

    header {
      margin-bottom: 2rem;
      border-bottom: 1px solid #1e2535;
      padding-bottom: 1.5rem;
    }

    header h1 {
      font-size: 1.6rem;
      font-weight: 700;
      color: #f8fafc;
      letter-spacing: -0.02em;
    }

    header p {
      margin-top: 0.5rem;
      color: #94a3b8;
      font-size: 0.9rem;
      line-height: 1.6;
    }

    .card {
      background: #161b27;
      border: 1px solid #1e2d40;
      border-radius: 12px;
      padding: 1.5rem;
      margin-bottom: 1.5rem;
    }

    .card-title {
      font-size: 0.8rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: #38bdf8;
      margin-bottom: 1.2rem;
    }

    label {
      display: block;
      font-size: 0.85rem;
      font-weight: 500;
      color: #cbd5e1;
      margin-bottom: 0.4rem;
    }

    .field { margin-bottom: 1.2rem; }
    .field:last-of-type { margin-bottom: 0; }

    select, input[type="text"] {
      width: 100%;
      padding: 0.6rem 0.8rem;
      background: #0f1117;
      border: 1px solid #2d3748;
      border-radius: 8px;
      color: #e2e8f0;
      font-size: 0.9rem;
      outline: none;
      transition: border-color 0.15s;
    }

    select:focus, input[type="text"]:focus {
      border-color: #38bdf8;
      box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.12);
    }

    select option { background: #1e2535; }

    button {
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      margin-top: 1.2rem;
      padding: 0.65rem 1.4rem;
      background: #0ea5e9;
      color: #fff;
      font-size: 0.9rem;
      font-weight: 600;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      transition: background 0.15s, transform 0.1s;
    }

    button:hover { background: #38bdf8; }
    button:active { transform: scale(0.98); }

    .error {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      margin-top: 1rem;
      padding: 0.75rem 1rem;
      background: rgba(239, 68, 68, 0.1);
      border: 1px solid rgba(239, 68, 68, 0.3);
      border-radius: 8px;
      color: #fca5a5;
      font-size: 0.875rem;
    }

    .section-label {
      font-size: 0.8rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: #38bdf8;
      margin-bottom: 0.6rem;
    }

    .section-desc {
      font-size: 0.85rem;
      color: #64748b;
      margin-bottom: 0.8rem;
      line-height: 1.5;
    }

    pre {
      background: #0a0d14;
      border: 1px solid #1e2535;
      border-radius: 8px;
      padding: 1.1rem 1.2rem;
      overflow-x: auto;
      font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
      font-size: 0.8rem;
      line-height: 1.7;
      color: #a5f3fc;
      white-space: pre;
    }

    .placeholder-text {
      color: #334155;
      font-style: italic;
    }

    footer {
      margin-top: 2rem;
      padding-top: 1.5rem;
      border-top: 1px solid #1e2535;
      text-align: center;
      font-size: 0.8rem;
      color: #475569;
    }

    footer a {
      color: #38bdf8;
      text-decoration: none;
    }

    footer a:hover { text-decoration: underline; }

    code {
      font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
      font-size: 0.82em;
      background: #0a0d14;
      border: 1px solid #1e2535;
      border-radius: 4px;
      padding: 0.1em 0.4em;
      color: #a5f3fc;
    }
  </style>
</head>
<body>
<div class="container">

  <header>
    <h1>Cisco ISR SIT + Message File Generator</h1>
    <p>Want to serve some older style telecom messages from your Cisco ISR? Well, here you go. Pick the SIT message you want up front
    then pick from the list of Pat Fleet messages and away you go.</p>

    <p>The generated file is a G.711 µ-law (ulaw) encoded mono AU file sampled at 8000 Hz — the native audio format
    for Cisco IOS. It is produced by prepending the selected SIT tone to the chosen message file and writing a single
    standard Sun AU header, making it ready to copy directly to the router's flash and reference in a VXML application.</p>

    <p>The Pat Fleet messages came from here: <a href="https://github.com/hharte/PatFleet-asterisk" target="_blank" rel="noopener noreferrer">https://github.com/hharte/PatFleet-asterisk</a>, so special thanks to them.</p>
  </header>

  <div class="card">
    <div class="card-title">Generate Audio File</div>

    <form method="post" action="/generate">
      <div class="field">
        <label for="sit_file">SIT tone file</label>
        <select name="sit_file" id="sit_file" required>
          <option value="" disabled selected>-- select a SIT tone --</option>
          {% for f in sit_files %}
          <option value="{{ f }}">{{ f }}</option>
          {% endfor %}
        </select>
      </div>

      <div class="field">
        <label for="au_file">AU message file</label>
        <input list="au_list" name="au_file" id="au_file"
               placeholder="start typing to filter…" autocomplete="off" required>
        <datalist id="au_list">
          {% for f in au_files %}
          <option value="{{ f }}">
          {% endfor %}
        </datalist>
      </div>

      <button type="submit">&#8681; Concatenate &amp; Download</button>
    </form>

    {% if error %}
    <div class="error">&#9888; {{ error }}</div>
    {% endif %}
  </div>

  <div class="card">
    <div class="section-label">Cisco IOS VXML Snippet</div>
    <p class="section-desc">Select both files above to generate a ready-to-use VXML app.</p>
    <pre id="vxml-preview"><span class="placeholder-text">&lt;!-- select a SIT tone and AU message file to populate --&gt;</span></pre>
  </div>

  <div class="card">
    <div class="section-label">Copying the File to Router Flash</div>
    <p class="section-desc">Once downloaded, host the AU file on a TFTP server accessible to the router, then copy it
    to flash using the following commands. Replace <code>192.168.1.10</code> with your TFTP server address and
    <code>your_file.au</code> with the downloaded filename.</p>
    <pre id="tftp-preview">router# copy tftp flash
Address or name of remote host []? 192.168.1.10
Source filename []? your_file.au
Destination filename [your_file.au]? flash:/audio/your_file.au</pre>
    <p class="section-desc" style="margin-top:0.8rem;">You can verify the file was copied successfully with:</p>
    <pre>router# dir flash:/audio/</pre>
  </div>

  <div class="card">
    <div class="section-label">Cisco IOS Configuration</div>
    <p class="section-desc">You may use the below text as a template for the IOS configuration (tested on IOS 15):</p>
    <pre>application
 ! example to play this file from flash
 ! make sure the file location in that vxml points to the correct location
 service your_service_name flash:/apps/your_xml_file.vxml
!
! dial-peer example
!
dial-peer voice 4240 voip
 ! make sure this points to the service registered above
 service your_service_name out-bound
 destination-pattern 4240
 session target loopback:rtp
 codec g711ulaw</pre>
  </div>

</div>

  <footer>
    <p>The source code for this app is available on GitHub at
      <a href="https://github.com/youngd24/cisco-isr-pfm" target="_blank" rel="noopener noreferrer">youngd24/cisco-isr-pfm</a>.
    </p>
  </footer>

  <script>
    const VXML_TEMPLATE = `<vxml version="2.0">
    <form>
        <field name="unusedField">
            <grammar type="application/grammar+regex">.</grammar>
            <prompt bargein="false" timeout="0s">
                <audio src="flash:/audio/AUFILE" />
            </prompt>
            <nomatch><disconnect /></nomatch>
            <noinput><disconnect /></noinput>
            <filled><disconnect /></filled>
        </field>
    </form>
</vxml>`;

    function stripExt(filename) {
      return filename.replace(/\\.au$/i, '');
    }

    function updatePreview() {
      const sitVal = document.getElementById('sit_file').value;
      const auVal  = document.getElementById('au_file').value.trim();
      const preview = document.getElementById('vxml-preview');
      const tftp    = document.getElementById('tftp-preview');

      if (!sitVal || !auVal) {
        preview.innerHTML = '<span class="placeholder-text">&lt;!-- select a SIT tone and AU message file to populate --&gt;</span>';
        tftp.textContent = `router# copy tftp flash\nAddress or name of remote host []? 192.168.1.10\nSource filename []? your_file.au\nDestination filename [your_file.au]? flash:/audio/your_file.au`;
        return;
      }

      const filename = stripExt(sitVal) + '_' + stripExt(auVal) + '.au';
      preview.textContent = VXML_TEMPLATE.replace('AUFILE', filename);
      tftp.textContent = `router# copy tftp flash\nAddress or name of remote host []? 192.168.1.10\nSource filename []? ${filename}\nDestination filename [${filename}]? flash:/audio/${filename}`;
    }

    document.getElementById('sit_file').addEventListener('change', updatePreview);
    document.getElementById('au_file').addEventListener('input', updatePreview);
  </script>
</body>
</html>'''


@app.route('/cisco-isr-pfm/')
def index():
    return render_template_string(
        TEMPLATE,
        sit_files=list_au_files(SIT_DIR),
        au_files=list_au_files(AU_DIR),
        error=None,
    )


@app.route('/generate', methods=['POST'])
def generate():
    sit_name = request.form.get('sit_file', '').strip()
    au_name  = request.form.get('au_file', '').strip()

    sit_path = os.path.realpath(os.path.join(SIT_DIR, sit_name))
    au_path  = os.path.realpath(os.path.join(AU_DIR,  au_name))

    # Guard against path traversal
    if not sit_path.startswith(os.path.realpath(SIT_DIR) + os.sep):
        return render_template_string(TEMPLATE,
            sit_files=list_au_files(SIT_DIR),
            au_files=list_au_files(AU_DIR),
            error="Invalid SIT file selection."), 400

    if not au_path.startswith(os.path.realpath(AU_DIR) + os.sep):
        return render_template_string(TEMPLATE,
            sit_files=list_au_files(SIT_DIR),
            au_files=list_au_files(AU_DIR),
            error="Invalid AU file selection."), 400

    if not os.path.isfile(sit_path):
        return render_template_string(TEMPLATE,
            sit_files=list_au_files(SIT_DIR),
            au_files=list_au_files(AU_DIR),
            error=f"SIT file not found: {sit_name}"), 400

    if not os.path.isfile(au_path):
        return render_template_string(TEMPLATE,
            sit_files=list_au_files(SIT_DIR),
            au_files=list_au_files(AU_DIR),
            error=f"AU file not found: {au_name}"), 400

    sit_stem = os.path.splitext(sit_name)[0]
    au_stem  = os.path.splitext(au_name)[0]
    download_name = f"{sit_stem}_{au_stem}.au"

    try:
        with tempfile.NamedTemporaryFile(suffix='.au', delete=False) as tmp:
            tmp_path = tmp.name

        concat_au(sit_path, au_path, tmp_path)

        return send_file(
            tmp_path,
            mimetype='audio/basic',
            as_attachment=True,
            download_name=download_name,
        )
    except ValueError as e:
        return render_template_string(TEMPLATE,
            sit_files=list_au_files(SIT_DIR),
            au_files=list_au_files(AU_DIR),
            error=str(e)), 400


if __name__ == '__main__':
    app.run(debug=True)
