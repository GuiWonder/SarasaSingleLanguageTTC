import os
import sys
import json
import re

gitenv=sys.argv[1]
md=open('README.md', 'r', encoding='utf-8').read()
pattern=re.compile(r"v[0-9\.]{1,}")
result=pattern.findall(md)
assert len(result)==1, result
lstver=result[0].strip('.')
print('The current version is', lstver)

os.system('curl -L https://api.github.com/repos/be5invis/Sarasa-Gothic/releases/latest -o rels.json')
rlss=json.load(open('rels.json', 'r', encoding = 'utf-8'))
rlstg=rlss['tag_name'].strip()

if lstver!=rlstg:
	print('Found the new version', rlstg)
	open('README.md', 'w', encoding='utf-8').write(md.replace(lstver, rlstg))
	open(gitenv, 'w', encoding='utf-8').write(f'hasnew=true\nversion={rlstg}\n')
else:
	print('No new version found.')
	open(gitenv, 'w', encoding='utf-8').write('hasnew=false')

