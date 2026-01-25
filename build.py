import os, json, logging, sys
from fontTools.ttLib import TTCollection
from shutil import rmtree

logging.basicConfig(
	level=logging.INFO,
	format="%(levelname)s: %(message)s",
	handlers=[logging.StreamHandler(sys.stdout),]
)

wts=['ExtraLight', 'Light', 'Regular', 'SemiBold', 'Bold']
loctgs=["CL", "SC", "TC", "HC", "J", "K"]
ishint=['', 'Unhinted-']

os.system('curl -L --ssl-no-revoke https://api.github.com/repos/be5invis/Sarasa-Gothic/releases/latest -o rels.json')
rlss=json.load(open('rels.json', 'r', encoding = 'utf-8'))
rlstg=rlss['tag_name']
rlsver=rlstg.replace('v', '')

def down(hint):
	zipfl='Sarasa-TTC-'+hint+rlsver+'.zip'
	ttcurl=f'https://github.com/be5invis/Sarasa-Gothic/releases/download/{rlstg}/{zipfl}'
	logging.info(f'Download Fonts {ttcurl}')
	os.system(f'wget {ttcurl}')
	os.system(f'7z e ./{zipfl} -o./tmp -aoa')
	os.remove(zipfl)

def build(hint):
	vttc= ['ft', 'ftit', 'fta']
	for t in loctgs: os.makedirs(t, exist_ok=True)
	for wt in wts:
		wk=dict()
		wtit='Italic' if wt=='Regular' else f'{wt}Italic'
		ftfile=f'./tmp/Sarasa-{wt}.ttc'
		itfile=f'./tmp/Sarasa-{wtit}.ttc'
		for l in loctgs:
			wk[l]=dict()
			for v in vttc:
				wk[l][v]=dict()
				wk[l][v]['ttc']=TTCollection()
			wk[l]['ft']['fl']=f'{l}/Sarasa-{l}-{wt}.ttc'
			wk[l]['ftit']['fl']=f'{l}/Sarasa-{l}-{wtit}.ttc'
			wk[l]['fta']['fl']=f'{l}/Sarasa-{l}-{wt}-with-Italic.ttc'
		logging.info(f'Loading {ftfile}')
		ttc=TTCollection(ftfile)
		logging.info(f'Loading {itfile}')
		ttcit=TTCollection(itfile)
		lenth=len(ttc.fonts)
		assert len(ttcit.fonts)==lenth
		logging.info('Processing')
		for i in range(lenth):
			font=ttc.fonts[i]
			fontit=ttcit.fonts[i]
			name=font['name'].getDebugName(6)
			for l in loctgs:
				if l in name:
					wk[l]['ft']['ttc'].fonts.append(font)
					wk[l]['ftit']['ttc'].fonts.append(fontit)
					wk[l]['fta']['ttc'].fonts.append(font)
					wk[l]['fta']['ttc'].fonts.append(fontit)
		logging.info('Save TTC')
		for l in loctgs:
			for v in vttc:
				outft=wk[l][v]['fl']
				logging.info(f'Saving {outft}')
				wk[l][v]['ttc'].save(outft)
		ttc.close()
		ttcit.close()
	logging.info('Build 7z files')
	for t in loctgs:
		zipfl=f'Sarasa{t}-TTC-{hint}{rlsver}.7z'
		logging.info(f'Build {zipfl}')
		os.system(f'7z a ./{zipfl} ./{t}/*.ttc -mx=9 -mfb=256 -md=512m')
		rmtree(f'./{t}')

for hint in ishint:
	os.makedirs('./tmp')
	down(hint)
	build(hint)
	rmtree('./tmp')
logging.info('End.')
