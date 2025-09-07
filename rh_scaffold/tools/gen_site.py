# gen_site.py | v1.0
import os, sys, yaml, glob, re
from pathlib import Path
def rel(a,b): return Path(os.path.relpath(b, start=a)).as_posix()
def list_md(globs_list):
    files=[]
    for g in globs_list: files += [Path(p) for p in glob.glob(g, recursive=True) if p.lower().endswith(".md")]
    return sorted(set(files), key=lambda p: p.as_posix())
def build_section_index(root, section):
    sd = root / section["path"]; sd.mkdir(parents=True, exist_ok=True)
    md_files = list_md(section.get("globs",[]))
    out = [f"# {section['title']}", ""]
    for f in md_files:
        if f.resolve() == (sd/"index.md").resolve(): continue
        out.append(f"- [{f.stem.replace('_',' ')}]({rel(sd,f)})")
    (sd/"index.md").write_text("\n".join(out)+"\n", encoding="utf-8")
def verify_relative_links(root):
    miss=[]
    for f in root.rglob("*.md"):
        txt=f.read_text(encoding="utf-8", errors="ignore")
        for m in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", txt):
            url=m.group(2).strip()
            if re.match(r"^https?://", url): continue
            if not (f.parent / url).resolve().exists(): miss.append((f,url))
    return miss
def main():
    cfg = Path(sys.argv[1]) if len(sys.argv)>1 else Path("site/km.site.yml")
    data = yaml.safe_load(cfg.read_text(encoding="utf-8")); root = Path(data["root"])
    for sec in data["sections"]: build_section_index(root, sec)
    out=["# "+data.get("site_name","KM"), ""]
    for sec in data["sections"]:
        idx = (root/sec["path"]/ "index.md")
        out.append(f"- [{sec['title']}]({rel(root, idx)})")
    (root/"index.md").write_text("\n".join(out)+"\n", encoding="utf-8")
    miss=verify_relative_links(root)
    if miss:
        print("BROKEN RELATIVE LINKS:"); [print(f" - {f}: {u}") for f,u in miss]; sys.exit(2)
    print("Site generated OK.")
if __name__=='__main__': main()
