import fs from 'fs';
import path from 'path';
import { createRequire } from 'module';

const require = createRequire(import.meta.url);
const mcpPath = 'C:\\Users\\liqingfeng\\AppData\\Local\\npm-global\\node_modules\\@cloudbase\\cloudbase-mcp\\dist\\index.cjs';
const { getCloudBaseManager } = require(mcpPath);

const ENV_ID = 'zy-feng-d3glt5d93b1a9f08e';

function loadEnvParams() {
  const envPath = path.join('d:\\ZY', 'code', 'backend', '.env');
  const vals = {};
  for (const line of fs.readFileSync(envPath, 'utf8').split(/\r?\n/)) {
    const t = line.trim();
    if (!t || t.startsWith('#') || !t.includes('=')) continue;
    const i = t.indexOf('=');
    vals[t.slice(0, i).trim()] = t.slice(i + 1).trim();
  }
  const params = {
    BAZI_DEBUG: 'false',
    BAZI_RAG_PROVIDER: 'http',
    BAZI_CURSOR_RUNTIME: 'cloud',
    BAZI_CURSOR_MODEL: vals.BAZI_CURSOR_MODEL || 'composer-2.5',
    BAZI_DEEPSEEK_BASE_URL: vals.BAZI_DEEPSEEK_BASE_URL || 'https://api.deepseek.com',
    BAZI_RAG_HTTP_URL: 'https://bazi-rag-262409-10-1437107927.sh.run.tcloudbase.com',
    BAZI_RAG_DEFAULT_CATEGORY: '01八字命理',
    BAZI_LIUYAO_RAG_CATEGORY: '02六爻卜筮',
    BAZI_MEIHUA_RAG_CATEGORY: '03梅花易学',
    BAZI_QIMEN_RAG_CATEGORY: '04奇门遁甲',
    BAZI_LIUREN_RAG_CATEGORY: '05大六壬',
    BAZI_KNOWLEDGE_DATA_DIR: '/app/knowledge/data',
    BAZI_KNOWLEDGE_ENABLED: 'true',
  };
  if (vals.BAZI_CURSOR_API_KEY) params.BAZI_CURSOR_API_KEY = vals.BAZI_CURSOR_API_KEY;
  if (vals.BAZI_DEEPSEEK_API_KEY) params.BAZI_DEEPSEEK_API_KEY = vals.BAZI_DEEPSEEK_API_KEY;
  return JSON.stringify(params);
}

async function deployService(manager, name, targetPath, serverConfig) {
  console.log(`[deploy] ${name} from ${targetPath}`);
  const result = await manager.cloudrun.deploy({
    serverName: name,
    targetPath,
    serverType: 'container',
    serverConfig,
  });
  console.log(`[ok] ${name}`, result?.RequestId || result?.status || 'triggered');
  return result;
}

async function main() {
  const manager = await getCloudBaseManager({
    cloudBaseOptions: { envId: ENV_ID },
    authStrategy: 'fail_fast',
  });
  if (!manager) {
    throw new Error('CloudBase manager init failed; run: node cli login');
  }

  await deployService(manager, 'bazi-rag', 'C:\\Users\\liqingfeng\\zy-code-rag', {
    Port: 8100,
    Dockerfile: 'Dockerfile',
    BuildDir: '.',
    OpenAccessTypes: ['PUBLIC', 'OA', 'MINIAPP'],
    Cpu: 2,
    Mem: 4,
    MinNum: 1,
    MaxNum: 1,
  });

  await deployService(manager, 'bazi-api', 'C:\\Users\\liqingfeng\\zy-code', {
    Port: 8080,
    Dockerfile: 'backend/Dockerfile',
    BuildDir: '.',
    OpenAccessTypes: ['PUBLIC', 'OA', 'MINIAPP'],
    Cpu: 0.5,
    Mem: 1,
    MinNum: 1,
    MaxNum: 1,
    EnvParams: loadEnvParams(),
  });
}

main().catch((err) => {
  console.error('[deploy failed]', err?.message || err);
  process.exit(1);
});
