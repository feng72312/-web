import fs from 'fs';
import path from 'path';
import { createRequire } from 'module';

const require = createRequire(import.meta.url);
const mcpPath =
  'C:\\Users\\liqingfeng\\AppData\\Local\\npm-global\\node_modules\\@cloudbase\\cloudbase-mcp\\dist\\index.cjs';
const { getCloudBaseManager } = require(mcpPath);

const ENV_ID = 'zy-feng-d3glt5d93b1a9f08e';
const SRC = path.join('d:\\ZY', 'code', 'rag');
const STAGING = 'C:\\Users\\liqingfeng\\zy-rag-deploy';
const COPY_NAMES = [
  'Dockerfile',
  '.dockerignore',
  'requirements-server.txt',
  'bazi_rag_engine.py',
  'server.py',
  'config.py',
  'categories.py',
  'reranker.py',
];

function prepareStaging() {
  fs.rmSync(STAGING, { recursive: true, force: true });
  fs.mkdirSync(STAGING, { recursive: true });
  for (const name of COPY_NAMES) {
    fs.copyFileSync(path.join(SRC, name), path.join(STAGING, name));
  }
  console.log('[staging]', STAGING, `(${COPY_NAMES.length} files, no chroma)`);
}

async function main() {
  prepareStaging();
  const manager = await getCloudBaseManager({
    cloudBaseOptions: { envId: ENV_ID },
    authStrategy: 'fail_fast',
  });
  if (!manager) throw new Error('CloudBase not logged in');

  console.log('[deploy] bazi-rag slim package + 4C/8G + InitialDelaySeconds=120');
  const result = await manager.cloudrun.deploy({
    serverName: 'bazi-rag',
    targetPath: STAGING,
    serverType: 'container',
    serverConfig: {
      Port: 8100,
      Dockerfile: 'Dockerfile',
      BuildDir: '.',
      OpenAccessTypes: ['PUBLIC', 'OA', 'MINIAPP'],
      Cpu: 4,
      Mem: 8,
      MinNum: 1,
      MaxNum: 1,
      InitialDelaySeconds: 120,
      EnvParams: JSON.stringify({
        RAG_CHROMA_DIR: '/mnt/chroma',
        RAG_RERANK: '0',
      }),
    },
  });
  console.log('[ok]', result?.RequestId || 'triggered');
}

main().catch((err) => {
  console.error('[deploy failed]', err?.message || err);
  process.exit(1);
});
