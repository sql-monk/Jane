// Exported declarations of web/admin/src as JSON for scripts/docs_reference.py (TypeScript compiler API).
// Usage: node scripts/docs_reference_ts.mjs  (needs `corepack pnpm --dir web/admin install`)
import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const admin = path.join(root, "web", "admin");
const require = createRequire(path.join(admin, "package.json"));
const ts = require("typescript");

const configPath = path.join(admin, "tsconfig.json");
const config = ts.readConfigFile(configPath, ts.sys.readFile);
const parsed = ts.parseJsonConfigFileContent(config.config, ts.sys, admin);
const program = ts.createProgram(parsed.fileNames, parsed.options);
const checker = program.getTypeChecker();

const src = path.join(admin, "src");
const skip = (file) =>
  !file.startsWith(src) ||
  file.includes(`${path.sep}generated${path.sep}`) ||
  /\.test\.tsx?$/.test(file) ||
  file.includes(`${path.sep}test${path.sep}`) ||
  file.endsWith(".d.ts");

const docOf = (symbol) => ts.displayPartsToString(symbol.getDocumentationComment(checker)).trim();
const flags = ts.TypeFormatFlags.NoTruncation | ts.TypeFormatFlags.UseFullyQualifiedType;
const short = (text, max = 400) => (text.length > max ? `${text.slice(0, max)} …` : text);

function membersOf(type) {
  return checker.getPropertiesOfType(type).map((prop) => {
    const decl = prop.valueDeclaration ?? prop.declarations?.[0];
    const propType = decl ? checker.getTypeOfSymbolAtLocation(prop, decl) : checker.getDeclaredTypeOfSymbol(prop);
    const modifiers = decl && ts.canHaveModifiers(decl) ? ts.getModifiers(decl) ?? [] : [];
    return {
      name: prop.getName(),
      type: checker.typeToString(propType, undefined, ts.TypeFormatFlags.NoTruncation),
      optional: (prop.flags & ts.SymbolFlags.Optional) !== 0,
      readonly: modifiers.some((m) => m.kind === ts.SyntaxKind.ReadonlyKeyword),
      doc: docOf(prop),
    };
  });
}

const modules = [];
for (const sf of program.getSourceFiles()) {
  const file = path.normalize(sf.fileName);
  if (skip(file)) continue;
  const moduleSymbol = checker.getSymbolAtLocation(sf);
  if (!moduleSymbol) continue;
  const rel = path.relative(src, file).replace(/\\/g, "/").replace(/\.tsx?$/, "");
  const exports = [];
  for (let symbol of checker.getExportsOfModule(moduleSymbol)) {
    if (symbol.flags & ts.SymbolFlags.Alias) symbol = checker.getAliasedSymbol(symbol);
    const decl = symbol.valueDeclaration ?? symbol.declarations?.[0];
    if (!decl || path.normalize(decl.getSourceFile().fileName) !== file) continue;
    const line = sf.getLineAndCharacterOfPosition(decl.getStart()).line + 1;
    const name = symbol.getName();
    const doc = docOf(symbol);
    let kind;
    let declaration;
    let members;
    if (ts.isInterfaceDeclaration(decl)) {
      kind = "interface";
      declaration = `interface ${name}${decl.typeParameters ? `<${decl.typeParameters.map((p) => p.getText()).join(", ")}>` : ""}`;
      if (decl.heritageClauses) declaration += ` ${decl.heritageClauses.map((h) => h.getText()).join(" ")}`;
      members = membersOf(checker.getDeclaredTypeOfSymbol(symbol));
    } else if (ts.isTypeAliasDeclaration(decl)) {
      kind = "type";
      declaration = short(decl.getText().replace(/^export\s+/, ""), 1200);
    } else if (ts.isEnumDeclaration(decl)) {
      kind = "enum";
      declaration = short(decl.getText().replace(/^export\s+/, ""), 1200);
    } else if (ts.isClassDeclaration(decl)) {
      kind = "class";
      declaration = `class ${name}${decl.heritageClauses ? ` ${decl.heritageClauses.map((h) => h.getText()).join(" ")}` : ""}`;
      members = membersOf(checker.getDeclaredTypeOfSymbol(symbol));
    } else {
      const type = checker.getTypeOfSymbolAtLocation(symbol, decl);
      const signatures = type.getCallSignatures();
      if (signatures.length) {
        const isComponent = /^[A-Z]/.test(name) && /\.tsx$/.test(file);
        kind = isComponent ? "component" : "function";
        declaration = signatures
          .map((s) => `function ${name}${checker.signatureToString(s, undefined, flags)}`.replace(/\): /, "): "))
          .join("\n");
      } else {
        kind = "variable";
        declaration = `const ${name}: ${short(checker.typeToString(type, undefined, ts.TypeFormatFlags.NoTruncation))}`;
      }
    }
    exports.push({ name, kind, line, doc, declaration, members });
  }
  if (!exports.length) continue;
  exports.sort((a, b) => a.line - b.line);
  const first = sf.statements[0];
  const jsDoc = first && ts.getJSDocCommentsAndTags(first).find((d) => ts.isJSDoc(d) && d.getStart() === first.getFullStart() + (first.getFullText().indexOf("/**")));
  modules.push({
    module: rel.replace(/\//g, "."),
    file: path.relative(root, file).replace(/\\/g, "/"),
    doc: jsDoc && typeof jsDoc.comment === "string" ? jsDoc.comment : "",
    exports,
  });
}
modules.sort((a, b) => a.module.localeCompare(b.module));
process.stdout.write(JSON.stringify(modules));
