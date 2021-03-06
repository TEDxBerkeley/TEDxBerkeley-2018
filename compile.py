"""Convert templates and configuration file into production HTML files."""

import jinja2
import os
import argparse
import json
import glob
import sass
import shutil
import itertools

from jsmin import jsmin

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('mode', type=str, choices=(
                    'production', 'staging', 'preview'))
parser.add_argument('--out', type=str,
                    help='Name of directory containing output', default='published')
parser.add_argument('--html', type=str,
                    help='Path to directory containing HTML templates',
                    default='./src/html')
parser.add_argument('--data', type=str,
                    help='Path to directory containing JSON data',
                    default='./src/data')
parser.add_argument('--global_json', type=str,
                    help='Path to directory containing global JSON data',
                    default='./src/data/global')
parser.add_argument('--sass', type=str,
                    help='Path to directory containing SASS',
                    default='./src/scss')
parser.add_argument('--static', type=str,
                    help='Path to directory containing statics',
                    default='./src/static')
parser.add_argument('--js', type=str,
                    help='Path to directory containing javascript',
                    default='./src/js')
parser.add_argument('--old', action='store_true',
                    help='generate old pages')
args = parser.parse_args()

os.makedirs(args.out, exist_ok=True)
os.makedirs(os.path.join(args.out, 'css'), exist_ok=True)
os.makedirs(os.path.join(args.out, 'js'), exist_ok=True)
env = jinja2.Environment(loader=jinja2.FileSystemLoader(args.html))

# Copy all static/ into dist folder.
for directory in (args.static,):
    target_directory = os.path.join(args.out, os.path.basename(directory))
    if os.path.exists(target_directory):
        shutil.rmtree(target_directory)
    shutil.copytree(directory, target_directory)

# Update CNAME if needed and copy
with open('CNAME', 'w') as cname:
    if args.mode == 'production':
        cname.write('tedxberkeley.org')
    elif args.mode == 'staging':
        cname.write('staging.tedxberkeley.org')
shutil.copy2('CNAME', os.path.join(args.out, 'CNAME'))

# Minify js
with open(os.path.join(args.js, 'script.js')) as js_file:
    with open(os.path.join(args.out, 'js', 'script.min.js'), 'w') as f:
        f.write(jsmin(js_file.read()))

# Compile css
with open(os.path.join(args.out, 'css', 'style.min.css'), 'w') as f:
    f.write(sass.compile(
        string=open(os.path.join(args.sass, 'style.scss')).read(),
        include_paths=[args.sass]))

# Generate global context
global_context = {}
for filepath in glob.iglob(os.path.join(args.global_json, '*.json')):
    key = os.path.basename(filepath).replace('.json', '')
    with open(filepath) as f:
        global_context[key] = json.load(f)

# Generate HTML from templates and JSON data

for filepath in itertools.chain(
        glob.iglob(os.path.join(args.html, '*.html')),
        glob.iglob(os.path.join(args.html, 'volunteer/*.html'))):
    datapath = filepath.replace(args.html, args.data) + '.json'
    context = global_context.copy()
    if os.path.exists(datapath):
        with open(datapath) as f:
            context.update(json.load(f))
    out_path = filepath.replace(args.html, args.out)
    if not out_path.endswith('index.html'):
        out_path = out_path.replace('.html', '/index.html')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    filename = filepath.replace(args.html, '')
    with open(out_path, 'w') as f:
        f.write(env.get_template(filename).render(context))

# Generate team member and speaker pages
team = json.load(open('src/data/global/team.json'))
speakers = json.load(open('src/data/global/speakers.json'))
template = env.get_template('templates/profile.html')
for member in team['2018'].values():
    context = global_context.copy()
    out = './published/about/%s/index.html' % member['name'].replace(' ', '-')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w') as f:
        context['person'] = member
        f.write(template.render(context))

for speaker in speakers['2018']:
    context = global_context.copy()
    out = './published/speakers/%s/index.html' % speaker['name'].replace(' ', '-')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w') as f:
        context['person'] = speaker
        f.write(template.render(context))

if args.old:

    year_template = env.get_template('templates/year.html')
    for year in range(2010, 2017):
        context = global_context.copy()
        out = './published/%d/index.html' % year
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, 'w') as f:
            context['year'] = year
            context['root'] = '/%d' % year
            context['speakers'] = speakers[str(year)]
            f.write(year_template.render(context))

    for year in range(2010, 2017):
        for speaker in speakers[str(year)]:
            context = global_context.copy()
            speaker_uri = speaker['name'].replace(' ', '-')
            out = './published/%d/speakers/%s/index.html' % (year, speaker_uri)
            os.makedirs(os.path.dirname(out), exist_ok=True)
            with open(out, 'w') as f:
                context['person'] = speaker
                context['root'] = '/%d' % year
                f.write(template.render(context))
