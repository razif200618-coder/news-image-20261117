// "One Day on Earth" — make.fun news-image-20261117 entry (Node 22, stdlib only).
// The entry image is the entry.png beside this file. The program copies it to
// the output directory make.fun hands it: MAKEFUN_OUTPUT_DIR outside the
// grader, /output inside it. No network, no drawing at run time — the same
// bytes are copied on every run, so both graded runs write identical files.
//
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(outDir, { recursive: true });
copyFileSync(join(here, 'entry.png'), join(outDir, 'entry.png'));
