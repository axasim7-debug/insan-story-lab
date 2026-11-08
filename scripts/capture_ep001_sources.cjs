const { chromium }=require('playwright');
const fs=require('fs');
const path=require('path');
const base=path.resolve(__dirname,'../episodes/EP001/assets');
fs.mkdirSync(`${base}/research`,{recursive:true});
fs.mkdirSync(`${base}/evidence`,{recursive:true});
const jobs=[
 ['baker-interview','https://www.digitalspy.com/tv/a150413/simon-baker-the-mentalist/','h1'],
 ['heller-audio-page','https://www.tvtimemachine.com/1333/interview-with-the-mentalist-creator-bruno-heller','h1'],
 ['bias-paper','https://pubmed.ncbi.nlm.nih.gov/22663351/','h1.heading-title'],
 ['baker-license','https://commons.wikimedia.org/wiki/File:Simon_Baker_on_set.jpg','#Licensing'],
 ['paley-record','https://www.paleycenter.org/collection/item?item=100013','h1']
];
(async()=>{
const b=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
const results=await Promise.all(jobs.map(async([id,url,selector])=>{
const p=await b.newPage({viewport:{width:1440,height:900}});
try{
const response=await p.goto(url,{waitUntil:'domcontentloaded',timeout:25000});
await p.locator(selector).first().scrollIntoViewIfNeeded({timeout:4000}).catch(()=>{});
const failed=(response?.status()??0)>=400;
const screenshotPath=failed?`evidence/blocked-${id}.png`:`research/${id}.png`;
await p.screenshot({path:`${base}/${screenshotPath}`});
const title=await p.title();
return {id,url,final_url:p.url(),http_status:response?.status(),title,path:screenshotPath,status:failed?'blocked_not_source_capture':'captured'};
}catch(e){return {id,url,status:'failed',error:e.message};}
finally{await p.close();}
}));
fs.writeFileSync(`${base}/SCREENSHOT_LOG.json`,JSON.stringify(results,null,2));results.forEach(x=>console.log(JSON.stringify(x)));await b.close();
})();
