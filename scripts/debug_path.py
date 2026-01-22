from pathlib import Path
p = Path('/nonexistent/directory')
print('repr:', repr(p))
print('str:', str(p))
print('exists:', p.exists())
print('is_dir:', p.is_dir())
print('absolute:', p.absolute())
print('resolve(strict=False):', p.resolve(strict=False))
