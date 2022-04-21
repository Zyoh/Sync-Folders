from pathlib import Path
import shutil
import sys
import os


def run(source_dir: Path, target_dir: Path = None):
	source_dir = Path(source_dir)
	if target_dir is None:
		target_dir = Path(__file__).parent / f"output_{source_dir.name}"
	else:
		target_dir = Path(target_dir)

	user_consent = input(f"-!-!- WARNING -!-!-\nThis will alter files located in {target_dir}\nOK? (y/[N])\n> ")
	if user_consent.strip().lower() not in ["y", "yes"]:
		return

	# Delete everything in target dir that isn't in here
	moved_files = []

	for source_fp in source_dir.rglob("*"):
		relative_fp = source_fp.relative_to(source_dir)
		target_fp = target_dir / relative_fp
		moved_files.append(relative_fp)

		# Only move if target doesn't exist or is outdated
		if (target_fp.exists() and os.path.getmtime(source_fp) > os.path.getmtime(target_fp))\
			or not target_fp.exists():
			print(f"Copying {relative_fp}")
			target_fp.parent.mkdir(parents=True, exist_ok=True)
			try:
				shutil.copy2(source_fp, target_fp)
			except PermissionError:
				pass

	# Delete files that shouldn't be there
	for fp in target_dir.rglob("*"):
		relative_fp = fp.relative_to(target_dir)
		if relative_fp not in moved_files:
			if not fp.exists():
				continue

			if fp.is_dir():
				print(f"Deleting directory {relative_fp}")
				shutil.rmtree(fp)
			else:
				print(f"Deleting file {relative_fp}")
				fp.unlink()


def main():
	if len(sys.argv) < 2:
		# error
		return 1
	else:
		source_dir, *target_dir = sys.argv[1:]
		if len(target_dir) > 0:
			target_dir = target_dir[0]
		else:
			target_dir = None

		run(source_dir, target_dir)


if __name__ == "__main__":
	main()
