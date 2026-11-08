from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parents[3]
out=root/'exports/EP001';out.mkdir(parents=True,exist_ok=True)
boards=[out/f'opening-{t}s.png' for t in [4,10,15,21]]
if '--refresh-boards' in sys.argv or not all(p.exists() for p in boards):
 subprocess.run(['node',str(Path(__file__).with_name('render-opening.cjs')),'--boards-only'],cwd=root,check=True)
cmd=['ffmpeg','-hide_banner','-loglevel','error','-y']
for p,duration in zip(boards,[7.4,6.4,5.4,6.4]):cmd+=['-loop','1','-t',str(duration),'-i',str(p)]
filters=[]
for n,label in enumerate('abcd'):
 filters.append(f'[{n}:v]fps=24,zoompan=z=1+0.000025*on:x=iw/2-iw/zoom/2:y=ih/2-ih/zoom/2:d=1:s=1920x1080:fps=24,format=yuv420p,setsar=1[{label}]')
filters+=['[a][b]xfade=transition=slideleft:duration=0.4:offset=7[ab]','[ab][c]xfade=transition=fade:duration=0.4:offset=13[abc]','[abc][d]xfade=transition=slideup:duration=0.4:offset=18,fade=t=out:st=23.5:d=0.5[v]']
cmd+=['-filter_complex_threads','1','-filter_complex',';'.join(filters),'-map','[v]','-t','24','-an','-c:v','libx264','-threads','2','-preset','veryfast','-crf','20','-movflags','+faststart','-metadata','comment=Silent visual treatment. Photo: Andrew Comings / CC BY 2.0. Not audio-synced.',str(out/'opening-visual-v1.mp4')]
subprocess.run(cmd,check=True)
print('Ready:',out/'opening-visual-v1.mp4')
