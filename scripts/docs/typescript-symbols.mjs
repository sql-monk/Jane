// TypeScript compiler API public-surface extraction. Source files are never evaluated.
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";
const root = path.resolve(process.argv[2] || ".");
let require = createRequire(import.meta.url);
let ts;
try {
  ts = require("typescript");
} catch {
  ts = createRequire(
    path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../web/admin/package.json"),
  )("typescript");
}
const sourceRoot = path.join(root, "web/admin/src");
const files = [];
function walk(dir) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const file = path.join(dir, entry.name);
    if (entry.isDirectory() && !["test", "__tests__", "node_modules"].includes(entry.name)) walk(file);
    else if (entry.isFile() && /\.(tsx?|mts)$/.test(entry.name) && !/\.(test|spec)\./.test(entry.name))
      files.push(file);
  }
}
walk(sourceRoot);
files.sort();
const program = ts.createProgram(files, {
  target: ts.ScriptTarget.ESNext,
  module: ts.ModuleKind.ESNext,
  moduleResolution: ts.ModuleResolutionKind.Bundler,
  jsx: ts.JsxEmit.ReactJSX,
  skipLibCheck: true,
  noEmit: true,
  allowJs: false,
  strict: true,
});
const checker = program.getTypeChecker();
const syntaxErrors = program.getSyntacticDiagnostics().filter((x) => files.includes(x.file?.fileName));
if (syntaxErrors.length)
  throw new Error(
    ts.formatDiagnostics(syntaxErrors, {
      getCanonicalFileName: (x) => x,
      getCurrentDirectory: () => root,
      getNewLine: () => "\n",
    }),
  );
const flags = ts.TypeFormatFlags.NoTruncation | ts.TypeFormatFlags.UseAliasDefinedOutsideCurrentScope;
const rel = (f) => path.relative(root, f).split(path.sep).join("/");
function location(node) {
  const source = node.getSourceFile();
  return {
    source: rel(source.fileName),
    line: source.getLineAndCharacterOfPosition(node.getStart(source)).line + 1,
    end_line: source.getLineAndCharacterOfPosition(node.getEnd()).line + 1,
  };
}
function privateMember(node) {
  return (
    (node.name && ts.isPrivateIdentifier(node.name)) ||
    (ts.getCombinedModifierFlags(node) & (ts.ModifierFlags.Private | ts.ModifierFlags.Protected)) !== 0
  );
}
function documentation(symbol) {
  return ts.displayPartsToString(symbol.getDocumentationComment(checker)) || null;
}
function signatureInfo(sig, node) {
  return {
    signature: checker.signatureToString(sig, node, flags),
    parameters: sig.getParameters().map((param) => {
      const decl = param.valueDeclaration || param.declarations?.[0] || node;
      return {
        name: param.name,
        type: checker.typeToString(checker.getTypeOfSymbolAtLocation(param, decl), decl, flags),
        default: decl.initializer?.getText() || null,
        kind: decl.dotDotDotToken ? "rest" : param.flags & ts.SymbolFlags.Optional ? "optional" : "required",
      };
    }),
    returns: checker.typeToString(sig.getReturnType(), node, flags),
  };
}
function record(symbol, declaration, id, parent = null) {
  const type = checker.getTypeOfSymbolAtLocation(symbol, declaration);
  const signatures = type.getCallSignatures().map((sig) => signatureInfo(sig, declaration));
  const props = {
    id,
    name: symbol.name,
    module: rel(declaration.getSourceFile().fileName)
      .replace(/^web\/admin\/src\//, "")
      .replace(/\.(tsx?|mts)$/, ""),
    component: "admin",
    language: "typescript",
    parent,
    ...location(declaration),
    docstring: documentation(symbol),
  };
  if (
    ts.isFunctionDeclaration(declaration) ||
    ts.isMethodDeclaration(declaration) ||
    ts.isMethodSignature(declaration)
  ) {
    const head = ts.isFunctionDeclaration(declaration) ? "function " : "";
    return {
      ...props,
      kind: parent ? "method" : "function",
      signature: head + symbol.name + (signatures[0]?.signature || declaration.getText().split("{")[0]),
      ...signatures[0],
      signature: head + symbol.name + (signatures[0]?.signature || "()"),
      overloads: signatures.slice(1).map((x) => head + symbol.name + x.signature),
      parameters: signatures[0]?.parameters || [],
      returns: signatures[0]?.returns || null,
    };
  }
  if (ts.isClassDeclaration(declaration) || ts.isInterfaceDeclaration(declaration)) {
    const bases = declaration.heritageClauses?.map((x) => x.getText()) || [];
    return {
      ...props,
      kind: ts.isClassDeclaration(declaration) ? "class" : "interface",
      bases,
      signature: `${ts.isClassDeclaration(declaration) ? "class" : "interface"} ${symbol.name}${declaration.typeParameters?.length ? "<" + declaration.typeParameters.map((x) => x.getText()).join(", ") + ">" : ""}${bases.length ? " " + bases.join(" ") : ""} {}`,
      members: [],
    };
  }
  if (ts.isEnumDeclaration(declaration))
    return { ...props, kind: "enum", signature: declaration.getText(), members: [] };
  if (ts.isTypeAliasDeclaration(declaration))
    return { ...props, kind: "type", signature: declaration.getText(), members: [] };
  if (ts.isGetAccessor(declaration) || ts.isSetAccessor(declaration)) {
    const declarations = symbol.declarations || [declaration];
    return {
      ...props,
      kind: "property",
      signature: `${symbol.name}: ${checker.typeToString(type, declaration, flags)}`,
      readable: declarations.some(ts.isGetAccessor),
      writable: declarations.some(ts.isSetAccessor),
      accessors: declarations
        .filter((x) => ts.isGetAccessor(x) || ts.isSetAccessor(x))
        .map((x) => x.getText().split("{")[0].trim()),
    };
  }
  const readonly = (ts.getCombinedModifierFlags(declaration) & ts.ModifierFlags.Readonly) !== 0;
  return {
    ...props,
    kind: parent ? "field" : symbol.name.toUpperCase() === symbol.name ? "constant" : "variable",
    signature: `${readonly ? "readonly " : ""}${symbol.name}${declaration.questionToken ? "?" : ""}: ${checker.typeToString(type, declaration, flags)}${declaration.initializer ? " = " + declaration.initializer.getText() : ""}`,
    annotation: checker.typeToString(type, declaration, flags),
    default: declaration.initializer?.getText() || null,
    readable: true,
    writable: !readonly,
    parameters: signatures[0]?.parameters || [],
    returns: signatures[0]?.returns || null,
    call_signatures: signatures.map((x) => symbol.name + x.signature),
  };
}
const symbols = [];
const inputs = [];
for (const file of files) {
  const source = program.getSourceFile(file);
  inputs.push(rel(file));
  if (!source.symbol) continue;
  const module = rel(file)
    .replace(/^web\/admin\/src\//, "")
    .replace(/\.(tsx?|mts)$/, "");
  for (const exported of checker.getExportsOfModule(source.symbol)) {
    const aliased = (exported.flags & ts.SymbolFlags.Alias) !== 0;
    const target = aliased ? checker.getAliasedSymbol(exported) : exported;
    const declaration = target.valueDeclaration || target.declarations?.[0];
    if (!declaration) throw new Error(`Export ${module}.${exported.name} has no declaration`);
    const id = `admin.${module.replaceAll("/", ".")}.${exported.name}`;
    const data = record(target, declaration, id);
    data.name = exported.name;
    data.module = module;
    if (aliased) {
      data.reexport = true;
      data.target = target.name;
      data.export_source = rel(file);
    }
    symbols.push(data);
    if (["class", "interface", "type", "enum"].includes(data.kind)) {
      const type =
        data.kind === "class" || data.kind === "interface"
          ? checker.getDeclaredTypeOfSymbol(target)
          : checker.getTypeOfSymbolAtLocation(target, declaration);
      for (const member of type.getProperties()) {
        const decl = member.valueDeclaration || member.declarations?.[0];
        if (!decl || privateMember(decl) || !rel(decl.getSourceFile().fileName).startsWith("web/admin/src/"))
          continue;
        const memberData = record(member, decl, `${id}.${member.name}`, id);
        memberData.module = module;
        const inherited = decl.parent !== declaration;
        symbols.push(memberData);
        data.members.push({ id: memberData.id, name: member.name, kind: memberData.kind, inherited });
      }
      if (ts.isClassDeclaration(declaration)) {
        for (const ctor of declaration.members
          .filter(ts.isConstructorDeclaration)
          .filter((x) => !privateMember(x))) {
          const sig = checker.getSignatureFromDeclaration(ctor);
          const info = signatureInfo(sig, ctor);
          const memberData = {
            ...data,
            id: id + ".constructor",
            name: "constructor",
            parent: id,
            kind: "constructor",
            ...location(ctor),
            ...info,
            signature: "constructor" + info.signature,
            docstring: null,
          };
          delete memberData.members;
          symbols.push(memberData);
          data.members.push({
            id: memberData.id,
            name: "constructor",
            kind: "constructor",
            inherited: false,
          });
        }
        // Static public fields and methods are not in the instance type.
        for (const member of declaration.members) {
          if (
            !(ts.getCombinedModifierFlags(member) & ts.ModifierFlags.Static) ||
            privateMember(member) ||
            !member.name
          )
            continue;
          const memberSymbol = checker.getSymbolAtLocation(member.name);
          if (!memberSymbol) continue;
          const memberData = record(memberSymbol, member, `${id}.${memberSymbol.name}`, id);
          memberData.static = true;
          memberData.module = module;
          symbols.push(memberData);
          data.members.push({
            id: memberData.id,
            name: memberSymbol.name,
            kind: memberData.kind,
            inherited: false,
          });
        }
      }
    }
  }
}
// Keep overload/accessor information in one symbol record.
const unique = new Map();
for (const symbol of symbols) unique.set(symbol.id, symbol);
process.stdout.write(
  JSON.stringify({
    parser: "typescript-compiler-api",
    version: ts.version,
    inputs,
    symbols: [...unique.values()].sort(
      (a, b) => a.module.localeCompare(b.module, "en") || a.line - b.line || a.id.localeCompare(b.id, "en"),
    ),
  }),
);
