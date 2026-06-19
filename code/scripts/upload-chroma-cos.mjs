import fs from 'fs';
import path from 'path';
import { createRequire } from 'module';

const require = createRequire(import.meta.url);
const mcpPath =
  'C:\\Users\\liqingfeng\\AppData\\Local\\npm-global\\node_modules\\@cloudbase\\cloudbase-mcp\\dist\\index.cjs';
const { getCloudBaseManager } = require(mcpPath);

const ENV_ID = 'zy-feng-d3glt5d93b1a9f08e';
const CHROMA_ROOT = path.join('d:\\ZY', 'code', 'rag', 'data', 'chroma');
const COS_PREFIX = 'data/chroma';

function walkFiles(dir, base = dir) {
  const out = [];
  for (const name of fs.readdirSync(dir)) {
    const full = path.join(dir, name);
    const st = fs.statSync(full);
    if (st.isDirectory()) {
      out.push(...walkFiles(full, base));
    } else {
      const rel = path.relative(base, full).split(path.sep).join('/');
      out.push({ localPath: full, cloudPath: `${COS_PREFIX}/${rel}` });
    }
  }
  return out;
}

async function main() {
  if (!fs.existsSync(path.join(CHROMA_ROOT, 'chroma.sqlite3'))) {
    throw new Error(`missing chroma index: ${CHROMA_ROOT}`);
  }
  const manager = await getCloudBaseManager({
    cloudBaseOptions: { envId: ENV_ID },
    authStrategy: 'fail_fast',
  });
  if (!manager) throw new Error('CloudBase not logged in');

  const storage = manager.storage;
  const files = walkFiles(CHROMA_ROOT);
  console.log(`[upload] ${files.length} files -> COS ${COS_PREFIX}/`);
  let done = 0;
  const batch = 200;
  for (let i = 0; i < files.length; i += batch) {
    const chunk = files.slice(i, i + batch);
    await storage.uploadFiles({
      files: chunk,
      parallel: 8,
      onFileFinish: () => {
        done += 1;
        if (done % 500 === 0 || done === files.length) {
          console.log(`[upload] ${done}/${files.length}`);
        }
      },
    });
  }
  console.log('[ok] chroma uploaded to COS mount path /mnt/chroma');
}

main().catch((err) => {
  console.error('[upload failed]', err?.message || err);
  process.exit(1);
});
