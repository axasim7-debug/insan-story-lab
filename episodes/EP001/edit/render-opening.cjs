const {chromium}=require('playwright');const http=require('http');const {spawn}=require('child_process');const path=require('path');const fs=require('fs');
(async()=>{
const root=path.resolve(__dirname,'../../..');const output=path.join(root,'exports/EP001');fs.mkdirSync(output,{recursive:true});
const server=http.createServer((req,res)=>{let file;if(req.url==='/fonts/bold.ttf')file='/usr/share/fonts/truetype/noto/NotoSansArabic-Bold.ttf';else if(req.url==='/fonts/regular.ttf')file='/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf';else {file=path.resolve(root,'.'+decodeURIComponent(req.url.split('?')[0]));if(!file.startsWith(root+path.sep)){res.writeHead(403);res.end();return;}}fs.readFile(file,(err,data)=>{if(err){res.writeHead(404);res.end();return;}const ext=path.extname(file);res.setHeader('Content-Type',({'.html':'text/html; charset=utf-8','.ttf':'font/ttf','.jpg':'image/jpeg'})[ext]||'application/octet-stream');res.end(data);});});await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--allow-file-access-from-files']});
const page=await browser.newPage({viewport:{width:1920,height:1080},deviceScaleFactor:1});
await page.goto(`http://127.0.0.1:${server.address().port}/episodes/EP001/edit/opening.html`);await page.evaluate(()=>window.ready);
for(const t of [4,10,15,21]){await page.evaluate(t=>renderFrame(t),t);await page.screenshot({path:path.join(output,`opening-${t}s.png`)});}
if(process.argv.includes('--boards-only')){await browser.close();server.close();console.log('Four 1080p boards exported.');return;}
const enc=spawn('ffmpeg',['-hide_banner','-loglevel','error','-y','-f','image2pipe','-vcodec','mjpeg','-framerate','24','-i','pipe:0','-an','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart','-metadata','comment=Silent visual treatment; timings provisional; photo Andrew Comings CC BY 2.0',path.join(output,'opening-visual-v1.mp4')],{stdio:['pipe','ignore','pipe']});
let err='';enc.stderr.on('data',x=>err+=x);const done=new Promise((resolve,reject)=>{enc.on('error',reject);enc.on('close',code=>code===0?resolve():reject(Error(err)))});
for(let f=0;f<576;f++){await page.evaluate(t=>renderFrame(t),f/24);const buf=await page.screenshot({type:'jpeg',quality:88});if(!enc.stdin.write(buf))await new Promise(res=>enc.stdin.once('drain',res));if(f%144===0)console.log(`Rendered ${f}/576`)}
enc.stdin.end();await done;await browser.close();server.close();console.log('Rendered 24s 1080p / 24 fps silent visual preview.');
})().catch(e=>{console.error(e.message);process.exit(1)});
