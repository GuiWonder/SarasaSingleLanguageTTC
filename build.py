import os, json
from afdko import otf2otc
from fontTools.ttLib import sfnt, TTFont
from shutil import copy, rmtree

wts=['ExtraLight', 'Light', 'Regular', 'SemiBold', 'Bold']
loctgs=["CL", "SC", "TC", "HC", "J", "K"]
allvars=['Gothic', 'UI', 'Mono', 'Mono-Slab', 'Term', 'Term-Slab', 'Fixed', 'Fixed-Slab']

ishint=['', 'Unhinted-']
os.system('curl -L https://api.github.com/repos/be5invis/Sarasa-Gothic/releases/latest -o rels.json')
rlss=json.load(open('rels.json', 'r', encoding = 'utf-8'))
rlstg=rlss['tag_name']
rlsver=rlstg.replace('v', '')

def get_psname(font):
	if 'name' in font:
		psname = font['name'].getDebugName(6)
		if psname:
			return psname

def tottf(ttc_path, keywd):
	with open(ttc_path, 'rb') as fp:
		num_fonts = sfnt.SFNTReader(fp, fontNumber=0).numFonts
	print(f'Input font: {os.path.basename(ttc_path)}\n')
	for ft_idx in range(num_fonts):
		font = TTFont(ttc_path, fontNumber=ft_idx, lazy=True)
		psname = get_psname(font)
		if keywd not in psname: continue
		if psname is None:
			ttc_name = os.path.splitext(os.path.basename(ttc_path))[0]
			psname = f'{ttc_name}-font{ft_idx}'

		ext = '.otf' if font.sfntVersion == 'OTTO' else '.ttf'
		font_filename = f'{psname}{ext}'
		print(f'Font {ft_idx}: {font_filename}')
		save_path = font_filename
		font.save(save_path)
		print(f'Saved {save_path}')
		font.close()

def dldft(hint):
	zipfl='Sarasa-TTC-'+hint+rlsver+'.zip'
	ttcurl=f'https://github.com/be5invis/Sarasa-Gothic/releases/download/{rlstg}/{zipfl}'
	print('Download Fonts', ttcurl)
	os.system(f'wget {ttcurl}')
	os.system(f'7z e ./{zipfl} -o./tmp -aoa')
	os.remove(zipfl)

def rettc(loctg, hint):
	for item in os.listdir('./tmp'):
		if item.lower().split('.')[-1]=='ttc':
			tottf(f'./tmp/{item}', loctg)
			# os.remove(item)
	print('Build TTC', loctg, hint)
	for wt in wts:
		ttc=f'Sarasa-{loctg}-{wt}.ttc'
		print('New TTC', ttc)
		fts=list()
		for v in allvars:
			fts.append(f'Sarasa-{v}-{loctg}-{wt}.ttf')
		print(fts)
		ttcarg=['-o', ttc]+fts
		otf2otc.run(ttcarg)
	print('Build TTC It', loctg, hint)
	for wt in wts:
		if wt=='Regular':
			wt='Italic'
		else:
			wt+='-Italic'
		ttc=f'Sarasa-{loctg}-{wt}.ttc'
		fts=list()
		for v in allvars:
			fts.append(f'Sarasa-{v}-{loctg}-{wt}.ttf')
		ttcarg=['-o', ttc]+fts
		otf2otc.run(ttcarg)
	print('Build TTC All', loctg, hint)
	for wt in wts:
		ttc=f'Sarasa-{loctg}-{wt}-with-Italic.ttc'
		fts=list()
		for v in allvars:
			fts.append(f'Sarasa-{v}-{loctg}-{wt}.ttf')
			if wt=='Regular':
				fts.append(f'Sarasa-{v}-{loctg}-Italic.ttf')
			else:
				fts.append(f'Sarasa-{v}-{loctg}-{wt}-Italic.ttf')
				
		ttcarg=['-o', ttc]+fts
		otf2otc.run(ttcarg)
	os.system(f'7z a ./Sarasa{loctg}-TTC-{hint}{rlsver}.7z ./*.ttc -mx=9 -mfb=256 -md=512m')

	for item in os.listdir('./'):
		if item.lower().split('.')[-1] in ['ttc', 'ttf', '.otf']:
			os.remove(item)

def build():
	for hint in ishint:
		os.makedirs('./tmp')
		dldft(hint)
		for loctg in loctgs:
			rettc(loctg, hint)
		rmtree('./tmp')

build()

