from pathlib import Path
import argparse,hashlib,json,re,html,subprocess
import xml.etree.ElementTree as ET

HERE=Path(__file__).resolve().parent
FW=HERE.parent.parent
parser=argparse.ArgumentParser(description='Render Knuckles layers from a compiled ZMK devicetree.')
parser.add_argument('--build-dir',type=Path,default=FW/'build/right-idle-test')
parser.add_argument('--out',type=Path,default=HERE)
options=parser.parse_args()
OUT=options.out.resolve();OUT.mkdir(parents=True,exist_ok=True)
geom=json.loads((HERE/'geometry.json').read_text())
compiled_path=options.build_dir/'zephyr/zephyr.dts'
compiled=compiled_path.read_text()
# Read actual compiled bindings rather than guessing from keymap source macros.
layernames=['default_layer','extra_layer','ctrl_layer','navi_layer']
layers=[]
for name in layernames:
 text=re.search(r'\b'+name+r'\s*\{\s*bindings\s*=\s*<(.*?)>;',compiled,re.S)[1]
 bindings=[]
 for name,args in re.findall(r'&(\w+)\s*([^&]*)',text):
  bindings.append((name,[int(x,0) for x in args.split()]))
 assert len(bindings)==54,(name,len(bindings))
 layers.append(bindings)
letters={0x70004+i:chr(65+i) for i in range(26)}
letters.update({0x7001e+i:str(i+1) for i in range(9)})
letters.update({0x70027:'0',0x70028:'Enter',0x70029:'Esc',0x7002a:'Bksp',0x7002b:'Tab',0x7002c:'Space',0x7002d:'−',0x7002e:'=',0x7002f:'[',0x70030:']',0x70031:'\\',0x70033:';',0x70034:"'",0x70035:'`',0x70036:',',0x70037:'.',0x70038:'/',0x7004a:'Home',0x7004b:'PgUp',0x7004d:'End',0x7004e:'PgDn',0x7004f:'→',0x70050:'←',0x70051:'↓',0x70052:'↑',0xc00b6:'Prev',0xc00b5:'Next',0xc00e2:'Mute',0xc00ea:'Vol −',0xc00e9:'Vol +',0xc00cd:'Play/Pause'})
letters.update({0x7003a+i:'F'+str(i+1) for i in range(12)})
mods={0x700e0:'Ctrl',0x700e1:'Shift',0x700e2:'Alt',0x700e3:'Cmd',0x700e4:'Ctrl',0x700e5:'Shift',0x700e6:'Alt',0x700e7:'Cmd'}
letters.update(mods)
names=['BASE','EXTRA','CTRL','NAVI']
colors=['#174b40','#8252ba','#276ec0','#227d63']
captions=['Typing · small lower legends show the action when held','Hold the left Space thumb key · tap that key for Space',"Hold the right apostrophe key · tap that key for '" ,'Hold the middle right thumb key']
def decode(binding):
 name,p=binding
 if name=='kp':return letters[p[0]],''
 if name=='mkp':return {1:'Left click',2:'Right click',4:'Middle click'}[p[0]],'hold to drag' if p[0]==1 else ''
 if name in ['hm','mt']:return letters[p[1]],'hold '+mods[p[0]]
 if name=='lt':return letters[p[1]],'hold '+names[p[0]]
 if name=='mo':return names[p[0]],'hold layer'
 if name=='gresc':return 'Esc / `',''
 if name=='bt':return ('BT '+str(p[1]+1),'select profile') if p[0]==3 else ('BT clear','current profile')
 if name=='studio_unlock':return 'Studio','unlock'
 if name=='soft_off':return 'Soft off',''
 raise ValueError(binding)
# Geometric layer indices use matrix addresses, not the order of PCB refs.
positions=[(r,c) for r in range(4) for c in range(12)]+[(4,c) for c in range(3,9)]
index={p:i for i,p in enumerate(positions)}
assert len(index)==54
edge_svg=ET.parse(HERE/'outline.svg').getroot()
edge_shapes=[]
for node in edge_svg.iter():
 tag=node.tag.split('}')[-1]
 if tag in ['path','circle','line','polyline']:
  attrs=' '.join(f'{key}="{html.escape(value,quote=True)}"' for key,value in node.attrib.items())
  edge_shapes.append(f'<{tag} {attrs}/>')
assert edge_shapes
xmin,ymin,width,height=geom['bounds']
poly=' '.join(f'{x},{-y}' for x,y in geom['tray_outline'])
SCALE=7.3

def text(x,y,value,size=3.0,fill='#193b32',weight='500',anchor='middle'):
 return f'<text x="{x:.3f}" y="{y:.3f}" text-anchor="{anchor}" font-size="{size}" font-weight="{weight}" fill="{fill}">{html.escape(value)}</text>'

def board(layer,side,x,y):
 # Position graphics with reflection, but keep legends readable in both halves.
 s=[f'<g transform="translate({x},{y}) scale({SCALE})">']
 if side=='left':transform=f'translate({-xmin}, {-ymin})'
 else:transform=f'translate({xmin+width}, {-ymin}) scale(-1,1)'
 s+=[f'<g transform="{transform}">',f'<polygon points="{poly}" fill="#e8efeb"/>','<g fill="none" stroke="#9cb7aa" stroke-width="0.28">',*edge_shapes,'</g>','</g>']
 for k in geom['keys']:
  col=k['col'] if side=='left' else 11-k['col'];i=index[k['row'],col]
  binding=layers[layer][i];inherited=binding[0]=='trans'
  if inherited:binding=layers[0][i]
  top,bottom=decode(binding)
  cx=k['x']-xmin if side=='left' else xmin+width-k['x'];cy=k['y']-ymin
  angle=k['angle'] if side=='left' else -k['angle']
  special=binding[0] in ['hm','mt','lt','mo']
  fill='#f3f6f4' if inherited else ('#e1eee8' if special and layer==0 else '#ffffff')
  border='#d2dfd8' if inherited else (colors[layer] if layer else '#b7cbbf')
  ink='#81958b' if inherited else '#193b32'
  secondary='#8ea197' if inherited else colors[layer]
  s.append(f'<rect x="{cx-8.1:.3f}" y="{cy-7.7:.3f}" width="16.2" height="15.4" rx="1.6" fill="{fill}" stroke="{border}" stroke-width="{.22 if inherited else .35}" transform="rotate({angle:.2f} {cx:.3f} {cy:.3f})"/>')
  size=3.9 if len(top)<=2 else 2.8 if len(top)<=6 else 2.25
  s.append(text(cx,cy+(.2 if bottom else 1.1),top,size,ink,'650' if not inherited else '400'))
  if bottom:s.append(text(cx,cy+3.8,bottom,1.65,secondary))
 s.append('</g>');return '\n'.join(s)

def header():
 return '<rect width="2400" height="4400" fill="#f8faf8"/>'+text(100,104,'KNUCKLES',66,weight='750',anchor='start')+text(100,162,'Your current layers · assembled 18.5 mm board · macOS modifier labels',29,'#597266',anchor='start')

def panel(layer,y):
 s=[f'<rect x="64" y="{y}" width="2272" height="970" rx="26" fill="white" stroke="#dce6df" stroke-width="2"/>']
 s+=[f'<rect x="100" y="{y+36}" width="76" height="53" rx="12" fill="{colors[layer]}"/>',text(138,y+74,str(layer),30,'white','700'),text(196,y+75,names[layer],38,colors[layer],'700','start'),text(196,y+120,captions[layer],25,'#597266',anchor='start')]
 s += [board(layer,'left',125,y+155),board(layer,'right',1275,y+155)]
 return '\n'.join(s)

svg='<svg xmlns="http://www.w3.org/2000/svg" width="2400" height="4400" viewBox="0 0 2400 4400"><g font-family="Arial, sans-serif">'+header()
for layer in range(4):svg+=panel(layer,225+layer*1000)
svg+=text(100,4290,'Gray legends inherit BASE. Colored borders mark layer overrides; green BASE keys have hold actions.',25,'#597266',anchor='start')
svg+=text(100,4338,'Source: compiled ZMK keymap · historical KiCad outline + switch matrix · EXTRA + F/D/S = left/right/middle click.',23,'#597266',anchor='start')+'</g></svg>'
(OUT/'knuckles-current-layers.svg').write_text(svg)
subprocess.run(['rsvg-convert','--output',str(OUT/'knuckles-current-layers.png'),str(OUT/'knuckles-current-layers.svg')],check=True)
for layer in range(4):
 svg='<svg xmlns="http://www.w3.org/2000/svg" width="2400" height="1120" viewBox="0 0 2400 1120"><rect width="2400" height="1120" fill="#f8faf8"/><g font-family="Arial, sans-serif">'+text(100,65,'KNUCKLES · '+names[layer],36,weight='700',anchor='start')+panel(layer,100)+'</g></svg>'
 path=OUT/f'{layer}-{names[layer].lower()}.svg';path.write_text(svg)
 subprocess.run(['rsvg-convert','--output',str(path.with_suffix('.png')),str(path)],check=True)
report={'firmware_commit':subprocess.check_output(['git','-C',str(FW),'rev-parse','HEAD'],text=True).strip(),'pcb_commit':'2a7e8daed7337c88100fd3420ae1bdc2f82260e8','pcb_file':'pcbs/knuckles_wireless.kicad_pcb','keys_per_half':27,'layers':layernames,'bindings_per_layer':54,'mouse_buttons_included':True,'uf2_sha256':hashlib.sha256((options.build_dir/'zephyr/zmk.uf2').read_bytes()).hexdigest(),'compiled_dts_sha256':hashlib.sha256(compiled_path.read_bytes()).hexdigest()}
(OUT/'sources.json').write_text(json.dumps(report,indent=2))
(OUT/'compiled-bindings.json').write_text(json.dumps(dict(zip(layernames,layers)),indent=2))

print(OUT)
